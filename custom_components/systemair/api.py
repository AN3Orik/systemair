"""API Client for Systemair VSR ventilation units using Modbus TCP."""

import asyncio
import contextlib
import socket
from abc import ABC, abstractmethod
from http import HTTPStatus
from typing import Any, NoReturn

import aiohttp
import async_timeout
import orjson
from pymodbus.client import AsyncModbusSerialClient, AsyncModbusTcpClient
from pymodbus.exceptions import ConnectionException

from .const import LOGGER
from .modbus import ModbusParameter, parameter_map

__all__ = [
    "ModbusConnectionError",
    "SystemairApiClientCommunicationError",
    "SystemairApiClientError",
    "SystemairAuthError",
    "SystemairAuthRequiredError",
    "SystemairClientBase",
    "SystemairModbusClient",
    "SystemairSerialClient",
    "SystemairWebApiClient",
]

# Plain-text status strings the IAM firmware returns instead of JSON.
# See the device-served scripts.js (>=IAM 1.4.0): ERROR, WRITE TMO, READ TMO,
# RESPONSE TMO, EMPTY, MB DISCONNECTED, OK.
_FIRMWARE_TRANSIENT_ERRORS = frozenset({"WRITE TMO", "READ TMO", "RESPONSE TMO", "EMPTY"})

MODBUS_DEVICE_BUSY_EXCEPTION = 6
MODBUS_GATEWAY_TARGET_FAILED_TO_RESPOND = 11
WEB_API_MAX_REGISTERS_PER_REQUEST = 70

READ_BLOCKS_BASE = [
    (1001, 62),
    (1101, 88),
    (1201, 74),
    (1351, 3),
    (1410, 10),
    (2001, 125),
    (2126, 24),
    (2201, 63),
    (2311, 8),
    (2401, 53),
    (2504, 18),
    (3002, 116),
    (4001, 12),
    (4101, 20),
    (7001, 6),
    (12011, 2),
    (12101, 41),
    (12301, 17),
    (12401, 5),
    (12544, 1),
    (14001, 4),
    (14101, 5),
    (14201, 4),
    (14301, 11),
    (14381, 1),
    (15901, 10),
]

READ_BLOCKS_ALARM_DETAILS = [
    (15016, 125),
    (15141, 125),
    (15266, 125),
    (15391, 125),
    (15516, 125),
]

READ_BLOCKS_ALARM_HISTORY = [
    (15641, 125),
    (15766, 125),
    (15891, 10),
]


class ModbusConnectionError(Exception):
    """Custom exception for connection errors."""


class SystemairApiClientError(Exception):
    """Exception to indicate a general API error."""


class SystemairApiClientCommunicationError(
    SystemairApiClientError,
):
    """Exception to indicate a communication error."""


class SystemairAuthError(SystemairApiClientError):
    """The IAM rejected the supplied password (HTTP 4xx from /auth/login)."""


class SystemairAuthRequiredError(SystemairApiClientError):
    """The IAM has no password configured yet — user must set one in the device UI."""


class _SessionExpiredError(Exception):
    """Internal signal: the current request hit an unauthenticated response."""


class SystemairClientBase(ABC):
    """Base class for Systemair API clients."""

    @abstractmethod
    async def test_connection(self) -> bool:
        """Test connection to the device."""

    @abstractmethod
    async def write_register(self, address_1based: int, value: int) -> None:
        """Write a single holding register."""

    @abstractmethod
    async def write_registers_32bit(self, address_1based: int, value: int) -> None:
        """Write a 32-bit value across two registers."""

    @abstractmethod
    async def get_all_data(
        self,
        *,
        enable_alarm_details: bool = True,
        enable_alarm_history: bool = False,
    ) -> dict[str, Any]:
        """Get all data from device."""


class SystemairModbusClient(SystemairClientBase):
    """Provides a client for interacting with a Systemair unit via Modbus TCP."""

    def __init__(self, host: str, port: int, slave_id: int, timeout: int = 5) -> None:
        """Initialize the Modbus client."""
        self._host = host
        self._port = port
        self._timeout = timeout
        self.slave_id = slave_id

        self._client: AsyncModbusTcpClient | None = None
        self._lock = asyncio.Lock()
        self._is_running = False
        self._worker_task: asyncio.Task | None = None
        self._request_queue: asyncio.Queue = asyncio.Queue()

    async def start(self) -> None:
        """Start the client and the background worker."""
        async with self._lock:
            if self._is_running:
                return
            self._is_running = True
            self._worker_task = asyncio.create_task(self._modbus_worker())
            LOGGER.info("Systemair Modbus client worker started.")

    async def stop(self) -> None:
        """Stop the client and the background worker."""
        async with self._lock:
            if not self._is_running:
                return
            self._is_running = False
            if self._worker_task:
                self._worker_task.cancel()
                with contextlib.suppress(asyncio.CancelledError):
                    await self._worker_task
            await self._close_connection()
            LOGGER.info("Systemair Modbus client worker stopped.")

    async def test_connection(self) -> bool:
        """Start, test a single read, and stop the client to validate connection."""
        try:
            await self.start()
            test_register_1based = parameter_map["REG_TC_SP"].register
            await self._queue_request("read", address=test_register_1based - 1, count=1)
        except (TimeoutError, ModbusConnectionError) as e:
            LOGGER.error("Failed to connect during test: %s", e)
            return False
        else:
            return True
        finally:
            await self.stop()

    async def _ensure_connected(self) -> None:
        """Ensure the client is connected, establishing connection if needed."""
        if self._client and self._client.connected:
            return

        LOGGER.debug("Connecting to Modbus device at %s:%s", self._host, self._port)
        self._client = AsyncModbusTcpClient(host=self._host, port=self._port, timeout=self._timeout)
        if not await self._client.connect():
            msg = f"Could not connect to VSR unit at {self._host}:{self._port}"
            raise ModbusConnectionError(msg)
        LOGGER.debug("Modbus connection successful.")

    async def _close_connection(self) -> None:
        """Close the Modbus connection."""
        if self._client:
            self._client.close()
            self._client = None
            LOGGER.debug("Modbus connection closed.")

    def _raise_unknown_request_type(self, request_type: str) -> NoReturn:
        """Raise ValueError for an unknown request type."""
        msg = f"Unknown request type: {request_type}"
        raise ValueError(msg)

    def _raise_unrecoverable_modbus_error(self, result: Any) -> NoReturn:
        """Raise ModbusConnectionError for unrecoverable errors."""
        msg = f"Unrecoverable Modbus error: {result}"
        raise ModbusConnectionError(msg)

    async def _execute_request(self, request_type: str, address: int, **kwargs: Any) -> list[int] | bool:
        """Execute a single Modbus request with robust retry and reconnect logic."""
        max_retries = 5
        base_delay = 0.2

        for attempt in range(max_retries):
            try:
                await self._ensure_connected()

                if request_type == "read":
                    count = kwargs.get("count", 1)
                    result = await self._client.read_holding_registers(address=address, count=count, device_id=self.slave_id)
                elif request_type == "write":
                    value = kwargs["value"]
                    result = await self._client.write_register(address=address, value=value, device_id=self.slave_id)
                elif request_type == "write_multiple":
                    values = kwargs["values"]
                    result = await self._client.write_registers(address=address, values=values, device_id=self.slave_id)
                else:
                    self._raise_unknown_request_type(request_type)

                if not result.isError():
                    return result.registers if request_type == "read" else True

                if result.exception_code in [
                    MODBUS_DEVICE_BUSY_EXCEPTION,
                    MODBUS_GATEWAY_TARGET_FAILED_TO_RESPOND,
                ]:
                    delay = base_delay * (2**attempt)
                    LOGGER.debug(
                        "Device busy/unresponsive (code %s) on %s. Retrying in %.2fs...",
                        result.exception_code,
                        request_type,
                        delay,
                    )
                    await asyncio.sleep(delay)
                else:
                    self._raise_unrecoverable_modbus_error(result)

            except (TimeoutError, ConnectionException, ModbusConnectionError) as e:
                LOGGER.warning("Connection error during %s: %s. Attempting to reconnect...", request_type, e)
                await self._close_connection()
                await asyncio.sleep(1)

            except Exception as e:
                LOGGER.error("Unexpected error during Modbus %s: %s", request_type, e, exc_info=True)
                raise

        msg = f"Failed to execute Modbus {request_type} after {max_retries} attempts."
        raise ModbusConnectionError(msg)

    async def _modbus_worker(self) -> None:
        """Process requests from the queue."""
        while self._is_running:
            try:
                request_type, address, future, kwargs = await self._request_queue.get()

                try:
                    result = await self._execute_request(request_type, address, **kwargs)
                    future.set_result(result)
                except (ModbusConnectionError, ValueError) as e:
                    future.set_exception(e)
                finally:
                    self._request_queue.task_done()
            except asyncio.CancelledError:
                break
        LOGGER.debug("Modbus worker shutting down.")

    async def _queue_request(self, request_type: str, address: int, **kwargs: Any) -> Any:
        """Add a request to the queue and wait for its completion."""
        if not self._is_running:
            msg = "Client is not running. Call start() first."
            raise ModbusConnectionError(msg)

        future = asyncio.Future()
        self._request_queue.put_nowait((request_type, address, future, kwargs))
        return await future

    async def write_register(self, address_1based: int, value: int) -> None:
        """Queue a write request for a single holding register."""
        await self._queue_request("write", address=address_1based - 1, value=value)

    async def write_registers_32bit(self, address_1based: int, value: int) -> None:
        """Queue a write request for a 32-bit value across two registers."""
        low_word = value & 0xFFFF
        high_word = value >> 16
        values = [low_word, high_word]
        await self._queue_request("write_multiple", address=address_1based - 1, values=values)

    async def get_all_data(
        self,
        *,
        enable_alarm_details: bool = True,
        enable_alarm_history: bool = False,
    ) -> dict[str, Any]:
        """Queue read requests for all required data blocks and assemble the result."""
        read_blocks = list(READ_BLOCKS_BASE)
        if enable_alarm_details:
            read_blocks.extend(READ_BLOCKS_ALARM_DETAILS)
        if enable_alarm_history:
            read_blocks.extend(READ_BLOCKS_ALARM_HISTORY)

        tasks = [self._queue_request("read", address=start - 1, count=count) for start, count in read_blocks]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        all_registers = {}
        has_successful_read = False
        for i, result in enumerate(results):
            start_addr_1based, _ = read_blocks[i]
            if isinstance(result, Exception):
                LOGGER.error(f"Failed to read block {start_addr_1based}: {result}")
                continue

            has_successful_read = True
            for offset, reg_val in enumerate(result):
                key = str(start_addr_1based - 1 + offset)
                all_registers[key] = reg_val

        if not has_successful_read:
            msg = "Failed to read any data blocks from the device."
            raise ModbusConnectionError(msg)

        return all_registers


class SystemairSerialClient(SystemairClientBase):
    """Provides a client for interacting with a Systemair unit via Modbus Serial (RS485)."""

    def __init__(  # noqa: PLR0913
        self,
        port: str,
        baudrate: int = 9600,
        bytesize: int = 8,
        parity: str = "N",
        stopbits: int = 1,
        slave_id: int = 1,
    ) -> None:
        """Initialize Modbus Serial client."""
        self._port = port
        self._baudrate = baudrate
        self._bytesize = bytesize
        self._parity = parity
        self._stopbits = stopbits
        self._slave_id = slave_id
        self._client: AsyncModbusSerialClient | None = None
        self._lock = asyncio.Lock()
        self._is_running = False
        self._worker_task: asyncio.Task | None = None
        self._request_queue: asyncio.Queue = asyncio.Queue()

    async def start(self) -> None:
        """Start the Modbus Serial client and worker task."""
        if self._is_running:
            LOGGER.debug("Serial client already running.")
            return

        self._is_running = True
        LOGGER.debug(
            "Initializing Modbus Serial client: port=%s, baudrate=%d, bytesize=%d, parity=%s, stopbits=%d, slave=%d",
            self._port,
            self._baudrate,
            self._bytesize,
            self._parity,
            self._stopbits,
            self._slave_id,
        )

        # Start worker task
        self._worker_task = asyncio.create_task(self._modbus_worker())
        LOGGER.info("Modbus Serial client started on %s", self._port)

    async def stop(self) -> None:
        """Stop the Modbus Serial client and close connection."""
        if not self._is_running:
            return

        LOGGER.debug("Stopping Modbus Serial client...")
        self._is_running = False

        # Cancel worker task
        if self._worker_task:
            self._worker_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._worker_task
            self._worker_task = None

        await self._close_connection()
        LOGGER.info("Modbus Serial client stopped.")

    async def _ensure_connection(self) -> None:
        """Ensure the Modbus Serial connection is established."""
        if self._client and self._client.connected:
            return

        LOGGER.debug("Establishing Modbus Serial connection on %s...", self._port)
        self._client = AsyncModbusSerialClient(
            port=self._port,
            baudrate=self._baudrate,
            bytesize=self._bytesize,
            parity=self._parity,
            stopbits=self._stopbits,
            timeout=10,
        )

        result = await self._client.connect()
        if not result:
            msg = f"Failed to connect to Modbus Serial device on {self._port}"
            raise ModbusConnectionError(msg)

        LOGGER.info("Modbus Serial connected on %s", self._port)

    async def _close_connection(self) -> None:
        """Close the Modbus Serial connection."""
        if self._client:
            LOGGER.debug("Closing Modbus Serial connection...")
            self._client.close()
            self._client = None

    def _raise_unrecoverable_modbus_error(self, result: Any) -> NoReturn:
        """Raise an error for unrecoverable Modbus exceptions."""
        msg = f"Modbus error code {result.exception_code}"
        raise ModbusConnectionError(msg)

    def _raise_unknown_request_type(self, request_type: str) -> NoReturn:
        """Raise an error for unknown request type."""
        msg = f"Unknown request type: {request_type}"
        raise ValueError(msg)

    async def _execute_request(self, request_type: str, address: int, **kwargs: Any) -> Any:
        """Execute a Modbus request with retry logic and exponential backoff."""
        max_retries = 5
        base_delay = 0.2

        for attempt in range(max_retries):
            delay = base_delay * (2**attempt)

            try:
                await self._ensure_connection()

                if request_type == "read":
                    count = kwargs.get("count", 1)
                    result = await self._client.read_holding_registers(address=address, count=count, device_id=self._slave_id)
                elif request_type == "write":
                    value = kwargs["value"]
                    result = await self._client.write_register(address=address, value=value, device_id=self._slave_id)
                elif request_type == "write_multiple":
                    values = kwargs["values"]
                    result = await self._client.write_registers(address=address, values=values, device_id=self._slave_id)
                else:
                    self._raise_unknown_request_type(request_type)

                if not result.isError():
                    return result.registers if request_type == "read" else True

                if result.exception_code in {MODBUS_DEVICE_BUSY_EXCEPTION, MODBUS_GATEWAY_TARGET_FAILED_TO_RESPOND}:
                    delay = base_delay * (2**attempt)
                    LOGGER.debug(
                        "Device busy/unresponsive (code %s) on %s. Retrying in %.2fs...",
                        result.exception_code,
                        request_type,
                        delay,
                    )
                    await asyncio.sleep(delay)
                else:
                    self._raise_unrecoverable_modbus_error(result)

            except (TimeoutError, ConnectionException, ModbusConnectionError) as e:
                LOGGER.warning("Connection error during %s: %s. Attempting to reconnect...", request_type, e)
                await self._close_connection()
                await asyncio.sleep(delay)

            except Exception as e:
                LOGGER.error("Unexpected error during Modbus %s: %s", request_type, e, exc_info=True)
                raise

        msg = f"Failed to execute Modbus {request_type} after {max_retries} attempts."
        raise ModbusConnectionError(msg)

    async def _modbus_worker(self) -> None:
        """Process requests from the queue."""
        while self._is_running:
            try:
                request_type, address, future, kwargs = await self._request_queue.get()

                try:
                    result = await self._execute_request(request_type, address, **kwargs)
                    future.set_result(result)
                except (ModbusConnectionError, ValueError) as e:
                    future.set_exception(e)
                finally:
                    self._request_queue.task_done()
            except asyncio.CancelledError:
                break
        LOGGER.debug("Modbus Serial worker shutting down.")

    async def _queue_request(self, request_type: str, address: int, **kwargs: Any) -> Any:
        """Add a request to the queue and wait for its completion."""
        if not self._is_running:
            msg = "Serial client is not running. Call start() first."
            raise ModbusConnectionError(msg)

        future = asyncio.Future()
        self._request_queue.put_nowait((request_type, address, future, kwargs))
        return await future

    async def write_register(self, address_1based: int, value: int) -> None:
        """Queue a write request for a single holding register."""
        await self._queue_request("write", address_1based - 1, value=value)

    async def write_registers_32bit(self, address_1based: int, value: int) -> None:
        """Queue a write request for a 32-bit value across two registers."""
        low_word = value & 0xFFFF
        high_word = (value >> 16) & 0xFFFF
        values = [low_word, high_word]
        await self._queue_request("write_multiple", address_1based - 1, values=values)

    async def test_connection(self) -> bool:
        """Test connection to the Modbus Serial device."""
        try:
            await self._ensure_connection()
            # Try to read a single register to verify communication
            result = await self._client.read_holding_registers(address=0, count=1, device_id=self._slave_id)
            return not result.isError()
        except (ModbusConnectionError, ConnectionException) as e:
            LOGGER.error("Serial connection test failed: %s", e)
            return False
        except OSError as e:
            LOGGER.error("Serial port error during connection test: %s", e)
            return False

    async def get_all_data(
        self,
        *,
        enable_alarm_details: bool = True,
        enable_alarm_history: bool = False,
    ) -> dict[str, Any]:
        """Queue read requests for all required data blocks and assemble the result."""
        read_blocks = list(READ_BLOCKS_BASE)
        if enable_alarm_details:
            read_blocks.extend(READ_BLOCKS_ALARM_DETAILS)
        if enable_alarm_history:
            read_blocks.extend(READ_BLOCKS_ALARM_HISTORY)

        tasks = [self._queue_request("read", address=start - 1, count=count) for start, count in read_blocks]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        all_registers = {}
        has_successful_read = False
        for i, result in enumerate(results):
            start_addr_1based, _ = read_blocks[i]
            if isinstance(result, Exception):
                LOGGER.error(f"Failed to read block {start_addr_1based}: {result}")
                continue

            has_successful_read = True
            for offset, reg_val in enumerate(result):
                key = str(start_addr_1based - 1 + offset)
                all_registers[key] = reg_val

        if not has_successful_read:
            msg = "Failed to read any data blocks from the device."
            raise ModbusConnectionError(msg)

        return all_registers


class SystemairWebApiClient(SystemairClientBase):
    """
    Systemair Web API Client for Modbus WebAPI.

    Handles the IP-pinned session auth introduced in IAM firmware 1.4.x:
    POST /auth/login with {"password": ...}, after which /mread and /mwrite
    accept requests from the same source IP. Older firmware that exposes the
    Modbus endpoints without auth still works when ``password`` is None.
    """

    def __init__(
        self,
        address: str,
        session: aiohttp.ClientSession,
        max_registers_per_request: int = WEB_API_MAX_REGISTERS_PER_REQUEST,
        password: str | None = None,
    ) -> None:
        """Systemair API Client."""
        self._address = address
        self._session = session
        self._lock = asyncio.Lock()
        self._max_registers_per_request = int(max_registers_per_request)
        self._password = password
        self._auth_lock = asyncio.Lock()
        self._authenticated = False

    @property
    def address(self) -> str:
        """Return the device address."""
        return self._address

    def set_password(self, password: str | None) -> None:
        """Update the stored password and force re-auth on the next request."""
        self._password = password
        self._authenticated = False

    async def async_test_connection(self) -> Any:
        """Test connection to API (legacy method for compatibility)."""
        return await self.test_connection()

    async def test_connection(self) -> bool:
        """
        Test connection to the device.

        Validates an authenticated read of a known register so we surface
        invalid-password problems here rather than during the first poll.
        """
        try:
            if self._password is not None:
                await self._ensure_authenticated(force=True)
                await self._api_wrapper(
                    method="get",
                    url=f"http://{self._address}/mread?{{%221130%22:1}}",
                    expects_data=True,
                )
            else:
                await self._api_wrapper(method="get", url=f"http://{self._address}/mread?{{}}")
        except (SystemairApiClientError, SystemairApiClientCommunicationError) as e:
            LOGGER.error("Failed to connect during test: %s", e)
            return False
        else:
            return True

    async def async_get_endpoint(self, endpoint: str) -> Any:
        """Get information from the API."""
        return await self._api_wrapper(method="get", url=f"http://{self._address}/{endpoint}")

    async def async_get_data(self, reg: list[ModbusParameter]) -> Any:
        """Read modbus registers."""
        async with self._lock:
            all_data = {}

            # Split large blocks into smaller chunks to avoid 414 URI Too Long error
            total_regs = len(reg)
            chunks_needed = int((total_regs + self._max_registers_per_request - 1) // self._max_registers_per_request)

            for chunk_idx in range(chunks_needed):
                start_idx = chunk_idx * self._max_registers_per_request
                end_idx = min(start_idx + self._max_registers_per_request, total_regs)
                chunk_regs = reg[start_idx:end_idx]

                query_params = ",".join(f"%22{item.register - 1}%22:1" for item in chunk_regs)
                url = f"http://{self._address}/mread?{{{query_params}}}"
                result = await self._api_wrapper(method="get", url=url, expects_data=True)
                all_data.update(result)

            return all_data

    async def async_set_data(self, registry: ModbusParameter, value: int) -> Any:
        """Write data to the API."""
        async with self._lock:
            query_params = f"%22{registry.register - 1}%22:{value}"
            url = f"http://{self._address}/mwrite?{{{query_params}}}"
            return await self._api_wrapper(method="get", url=url, expects_data=True)

    async def write_register(self, address_1based: int, value: int) -> None:
        """Write a single holding register (compatibility with Modbus TCP client)."""
        async with self._lock:
            query_params = f"%22{address_1based - 1}%22:{value}"
            url = f"http://{self._address}/mwrite?{{{query_params}}}"
            await self._api_wrapper(method="get", url=url, expects_data=True)

    async def write_registers_32bit(self, address_1based: int, value: int) -> None:
        """Write a 32-bit value across two registers (compatibility with Modbus TCP client)."""
        async with self._lock:
            low_word = value & 0xFFFF
            high_word = (value >> 16) & 0xFFFF

            # Write both registers: low word first, then high word
            query_params = f"%22{address_1based - 1}%22:{low_word},%22{address_1based}%22:{high_word}"
            url = f"http://{self._address}/mwrite?{{{query_params}}}"
            await self._api_wrapper(method="get", url=url, expects_data=True)

    async def get_all_data(
        self,
        *,
        enable_alarm_details: bool = True,
        enable_alarm_history: bool = False,
    ) -> dict[str, Any]:
        """Get all data from device (compatibility with Modbus TCP client)."""
        async with self._lock:
            read_blocks = list(READ_BLOCKS_BASE)
            if enable_alarm_details:
                read_blocks.extend(READ_BLOCKS_ALARM_DETAILS)
            if enable_alarm_history:
                read_blocks.extend(READ_BLOCKS_ALARM_HISTORY)

            tasks = []
            for start, count in read_blocks:
                tasks.append(self._read_block(start, count))

            results = await asyncio.gather(*tasks, return_exceptions=True)

            all_registers = {}
            has_successful_read = False

            for i, result in enumerate(results):
                start_addr_1based, _ = read_blocks[i]
                if isinstance(result, Exception):
                    LOGGER.error(f"Failed to read block {start_addr_1based}: {result}")
                    continue

                has_successful_read = True
                all_registers.update(result)

            if not has_successful_read:
                msg = "Failed to read any data blocks from the device."
                raise ModbusConnectionError(msg)

            return all_registers

    async def _read_block(self, start: int, count: int) -> dict[str, Any]:
        """Read a single block of registers, splitting into smaller chunks if needed to avoid URL length limit."""
        all_data = {}

        # Split large blocks into smaller chunks to avoid 414 URI Too Long error
        chunks_needed = int((count + self._max_registers_per_request - 1) // self._max_registers_per_request)

        for chunk_idx in range(chunks_needed):
            chunk_start = start + (chunk_idx * self._max_registers_per_request)
            chunk_count = min(self._max_registers_per_request, count - (chunk_idx * self._max_registers_per_request))

            # Build list of registers for this chunk
            regs = [chunk_start - 1 + offset for offset in range(chunk_count)]

            # Build query params
            query_params = ",".join(f"%22{reg}%22:1" for reg in regs)
            url = f"http://{self._address}/mread?{{{query_params}}}"

            try:
                result = await self._api_wrapper(method="get", url=url, expects_data=True)
                # Convert result to match Modbus TCP format (string keys)
                all_data.update({str(k): v for k, v in result.items()})
            except SystemairAuthError:
                raise
            except SystemairAuthRequiredError:
                raise
            except SystemairApiClientError as e:
                msg = f"Failed to read block chunk starting at {chunk_start}: {e}"
                raise ModbusConnectionError(msg) from e

        return all_data

    async def _ensure_authenticated(self, *, force: bool = False) -> None:
        """
        Log in to /auth/login if a password is configured and we're not already authed.

        No-op when ``self._password`` is None (older firmware that doesn't gate
        the Modbus endpoints). Raises ``SystemairAuthRequiredError`` if the
        device reports no password is configured yet, ``SystemairAuthError``
        if the supplied password is rejected.
        """
        if self._password is None:
            return

        async with self._auth_lock:
            if self._authenticated and not force:
                return

            status_url = f"http://{self._address}/auth/status"
            try:
                async with async_timeout.timeout(10):
                    response = await self._session.get(status_url)
                    status_payload = await response.json(content_type=None)
            except (TimeoutError, aiohttp.ClientError, ValueError, orjson.JSONDecodeError) as exception:
                msg = f"Failed to query /auth/status: {exception}"
                raise SystemairApiClientCommunicationError(msg) from exception

            if not status_payload.get("configured", False):
                msg = "No password is configured on the device. Set one in the IAM web UI first."
                raise SystemairAuthRequiredError(msg)

            login_url = f"http://{self._address}/auth/login"
            try:
                async with async_timeout.timeout(10):
                    response = await self._session.post(
                        login_url,
                        json={"password": self._password},
                        headers={"Content-Type": "application/json"},
                    )
            except (TimeoutError, aiohttp.ClientError) as exception:
                msg = f"Failed to POST /auth/login: {exception}"
                raise SystemairApiClientCommunicationError(msg) from exception

            if response.status >= HTTPStatus.BAD_REQUEST:
                self._authenticated = False
                body = await response.text()
                msg = f"Device rejected password (HTTP {response.status}): {body}"
                raise SystemairAuthError(msg)

            self._authenticated = True
            LOGGER.debug("Authenticated against %s", self._address)

    async def _parse_response(
        self,
        response: aiohttp.ClientResponse,
        *,
        retry: bool,
        expects_data: bool,
    ) -> Any:
        """
        Parse the response.

        Raises ``_SessionExpiredError`` when the device replies with a payload that
        looks like an unauthenticated rejection (literal body ``ERROR`` or an
        empty ``{}`` for a request that asked for register data). The caller
        in ``_api_wrapper`` reacts by re-running ``_ensure_authenticated``
        once and retrying.
        """
        response_body = await response.text()
        stripped = response_body.strip() if response_body else ""

        if not stripped:
            LOGGER.warning("Received empty response from device")
            if not retry:
                msg = "Empty response from device"
                raise SystemairApiClientCommunicationError(msg)
            await asyncio.sleep(1)
            return None

        if "MB DISCONNECTED" in response_body:
            LOGGER.debug("Received 'MB DISCONNECTED', retrying...")
            if not retry:
                msg = "MB DISCONNECTED"
                raise SystemairApiClientCommunicationError(msg)
            await asyncio.sleep(1)
            return None

        if stripped == "ERROR":
            # Generic firmware error; on session-gated endpoints this is also
            # the response we get when the IP is no longer authenticated, so
            # let _api_wrapper try a forced re-auth before giving up.
            msg_0 = "Device returned ERROR"
            raise _SessionExpiredError(msg_0)

        if stripped in _FIRMWARE_TRANSIENT_ERRORS:
            LOGGER.debug("Received firmware transient error '%s', retrying...", stripped)
            if not retry:
                msg = stripped
                raise SystemairApiClientCommunicationError(msg)
            await asyncio.sleep(1)
            return None

        if "OK" in response_body:
            return response_body

        try:
            payload = await response.json(content_type=None)
        except (ValueError, orjson.JSONDecodeError) as e:
            LOGGER.warning("Failed to parse JSON response. Body: %s", response_body)
            if not retry:
                msg = f"Invalid JSON response: {e}"
                raise SystemairApiClientCommunicationError(msg) from e
            await asyncio.sleep(1)
            return None

        if expects_data and isinstance(payload, dict) and not payload:
            # The caller asked for register data but the server returned `{}`.
            # That's how the firmware responds to /mread when the source IP is
            # not authenticated.
            msg_0 = "Empty register payload — likely session expired"
            raise _SessionExpiredError(msg_0)

        return payload

    async def _api_wrapper(  # noqa: PLR0912, PLR0915
        self,
        method: str,
        url: str,
        data: dict | None = None,
        headers: dict | None = None,
        *,
        expects_data: bool = False,
    ) -> Any:
        """
        Get information from the API with robust retry logic.

        ``expects_data=True`` enables session-expiry detection: when the device
        replies with ``ERROR`` or an empty ``{}`` body, this forces a fresh
        ``/auth/login`` and retries the request once.
        """
        max_retries = 5
        base_delay = 0.2
        reauth_attempts = 0

        if expects_data:
            await self._ensure_authenticated()

        for attempt in range(max_retries):
            try:
                async with async_timeout.timeout(10):
                    response = await self._session.request(
                        method=method,
                        url=url,
                        headers=headers,
                        json=data,
                    )
                    parsed_response = await self._parse_response(
                        response,
                        retry=attempt < max_retries - 1,
                        expects_data=expects_data,
                    )

                    if parsed_response is None:
                        # MB DISCONNECTED - retry with exponential backoff
                        delay = base_delay * (2**attempt)
                        LOGGER.debug(
                            "Device disconnected on attempt %d/%d. Retrying in %.2fs...",
                            attempt + 1,
                            max_retries,
                            delay,
                        )
                        await asyncio.sleep(delay)
                        continue

                    return parsed_response

            except _SessionExpiredError as exception:
                # Try to re-authenticate at most once per request, then retry.
                if self._password is None or reauth_attempts >= 1:
                    msg = f"Device returned an unauthenticated response: {exception}"
                    raise SystemairAuthError(msg) from exception
                reauth_attempts += 1
                LOGGER.info("Session looks expired against %s — re-authenticating", self._address)
                await self._ensure_authenticated(force=True)
                continue

            except TimeoutError as exception:
                if attempt < max_retries - 1:
                    delay = base_delay * (2**attempt)
                    LOGGER.warning(
                        "Timeout on attempt %d/%d: %s. Retrying in %.2fs...",
                        attempt + 1,
                        max_retries,
                        exception,
                        delay,
                    )
                    await asyncio.sleep(delay)
                    continue
                msg = f"Timeout error after {max_retries} attempts - {exception}"
                raise SystemairApiClientCommunicationError(msg) from exception

            except (aiohttp.ClientError, socket.gaierror) as exception:
                if attempt < max_retries - 1:
                    delay = base_delay * (2**attempt)
                    LOGGER.warning(
                        "Connection error on attempt %d/%d: %s. Retrying in %.2fs...",
                        attempt + 1,
                        max_retries,
                        exception,
                        delay,
                    )
                    await asyncio.sleep(delay)
                    continue
                msg = f"Connection error after {max_retries} attempts - {exception}"
                raise SystemairApiClientCommunicationError(msg) from exception

            except SystemairApiClientCommunicationError:
                # Retry communication errors (MB DISCONNECTED, empty response, invalid JSON)
                if attempt < max_retries - 1:
                    delay = base_delay * (2**attempt)
                    LOGGER.warning(
                        "Communication error on attempt %d/%d. Retrying in %.2fs...",
                        attempt + 1,
                        max_retries,
                        delay,
                    )
                    await asyncio.sleep(delay)
                    continue
                raise

            except (SystemairAuthError, SystemairAuthRequiredError):
                raise

            except Exception as exception:  # pylint: disable=broad-except
                LOGGER.error("Unexpected error during API request: %s", exception, exc_info=True)
                msg = f"Unexpected error - {exception}"
                raise SystemairApiClientError(msg) from exception

        msg = f"Failed to execute API request after {max_retries} attempts"
        raise SystemairApiClientError(msg)

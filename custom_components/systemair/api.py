"""API Client for Systemair VSR ventilation units using Modbus TCP."""

import asyncio
import contextlib
from typing import Any, NoReturn

from pymodbus.client import AsyncModbusTcpClient
from pymodbus.exceptions import ConnectionException

from .const import LOGGER
from .modbus import parameter_map

MODBUS_DEVICE_BUSY_EXCEPTION = 6
MODBUS_GATEWAY_TARGET_FAILED_TO_RESPOND = 11


class ModbusConnectionError(Exception):
    """Custom exception for connection errors."""


class SystemairVSRModbusClient:
    """Provides a client for interacting with a Systemair VSR unit."""

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
                    result = await self._client.read_holding_registers(address=address, count=kwargs["count"], device_id=self.slave_id)
                elif request_type == "write":
                    result = await self._client.write_register(address=address, value=kwargs["value"], device_id=self.slave_id)
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

    async def get_all_data(self) -> dict[str, Any]:
        """Queue read requests for all required data blocks and assemble the result."""
        read_blocks = [
            (1001, 62),
            (1101, 80),
            (1271, 4),
            (1353, 1),
            (2001, 50),
            (2505, 1),
            (3002, 116),
            (4001, 12),
            (4100, 1),
            (7005, 2),
            (12102, 40),
            (12306, 12),
            (12401, 2),
            (12544, 1),
            (14001, 4),
            (14101, 5),
            (14201, 2),
            (14381, 1),
            (15016, 125),
            (15141, 125),
            (15266, 125),
            (15391, 125),
            (15516, 125),
            (15641, 125),
            (15766, 125),
            (15891, 13),
        ]

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

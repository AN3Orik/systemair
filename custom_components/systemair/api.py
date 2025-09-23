"""API Client for Systemair VSR ventilation units using Modbus TCP."""

import asyncio
from typing import Any

from pymodbus.client import AsyncModbusTcpClient
from pymodbus.exceptions import ModbusException

from .const import LOGGER
from .modbus import parameter_map

MODBUS_DEVICE_BUSY_EXCEPTION = 6


class ModbusConnectionError(Exception):
    """Custom exception for connection errors."""


class SystemairVSRModbusClient:
    """Provides a client for interacting with a Systemair VSR unit via Modbus."""

    def __init__(self, host: str, port: int, slave_id: int, timeout: int = 5) -> None:
        """Initialize the Modbus client."""
        self._client = AsyncModbusTcpClient(host, port=port, timeout=timeout)
        self.slave_id = slave_id
        self._lock = asyncio.Lock()
        self._is_connected = False

    async def close(self) -> None:
        """Close the Modbus connection."""
        if self._is_connected:
            self._client.close()
            self._is_connected = False

    async def _ensure_connected(self) -> None:
        """Ensure the client is connected, establishing connection if needed."""
        if not self._is_connected:
            self._is_connected = await self._client.connect()
            if not self._is_connected:
                msg = "Could not connect to VSR unit"
                raise ModbusConnectionError(msg)

    async def test_connection(self) -> bool:
        """Test the connection to the Modbus device."""
        async with self._lock:
            try:
                await self._ensure_connected()
                test_register_1based = parameter_map["REG_TC_SP"].register
                await self._client.read_holding_registers(address=test_register_1based - 1, count=1, device_id=self.slave_id)
            except (ModbusException, ModbusConnectionError) as e:
                LOGGER.error("Failed to connect during test: %s", e)
                return False
            else:
                return True
            finally:
                await self.close()

    async def write_register(self, address_1based: int, value: int) -> None:
        """Write a single holding register with retry logic."""
        max_retries = 3
        retry_delay = 0.3

        async with self._lock:
            last_exception = None
            for attempt in range(max_retries):
                try:
                    await self._ensure_connected()
                    result = await self._client.write_register(address=address_1based - 1, value=value, device_id=self.slave_id)
                    if not result.isError():
                        LOGGER.debug(f"Successfully wrote {value} to register {address_1based}")
                        return

                    last_exception = result
                    LOGGER.debug(f"Write error on register {address_1based}, attempt {attempt + 1}: {result}")

                except ModbusException as e:
                    last_exception = e
                    LOGGER.debug(f"Write exception on register {address_1based}, attempt {attempt + 1}: {e}")

                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay)

            msg = f"Failed to write to register {address_1based} after {max_retries} attempts: {last_exception}"
            await self.close()
            raise ModbusConnectionError(msg)

    async def get_all_data(self) -> dict[str, Any]:
        """Read all required registers using a robust, paced, and fault-tolerant approach."""
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

        all_registers = {}
        max_retries = 3
        retry_delay = 0.3

        async with self._lock:
            await self._ensure_connected()
            for start_addr_1based, count in read_blocks:
                block_success = False
                for attempt in range(max_retries):
                    try:
                        result = await self._client.read_holding_registers(
                            address=start_addr_1based - 1, count=count, device_id=self.slave_id
                        )

                        if not result.isError():
                            for i, reg_val in enumerate(result.registers):
                                key = str(start_addr_1based - 1 + i)
                                all_registers[key] = reg_val
                            block_success = True
                            break

                        LOGGER.debug(f"Modbus error on block {start_addr_1based}, attempt {attempt + 1}: {result}. Retrying...")

                    except ModbusException as e:
                        LOGGER.debug(f"Modbus exception on block {start_addr_1based}, attempt {attempt + 1}: {e}. Retrying...")

                    if attempt < max_retries - 1:
                        await asyncio.sleep(retry_delay)

                if not block_success:
                    LOGGER.error(f"Failed to read block {start_addr_1based} after {max_retries} attempts. Continuing with next blocks.")

                await asyncio.sleep(0.15)

        if not all_registers:
            msg = "Failed to read any data from the device after multiple retries."
            raise ModbusConnectionError(msg)

        return all_registers

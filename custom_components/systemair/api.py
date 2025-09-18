"""API Client for Systemair VSR ventilation units using Modbus TCP."""
import asyncio
from typing import Any

from pymodbus.client import AsyncModbusTcpClient
from pymodbus.exceptions import ModbusException

from .const import LOGGER
from .modbus import parameter_map


class ModbusConnectionError(Exception):
    """Custom exception for connection errors."""


class SystemairVSRModbusClient:
    """Provides a client for interacting with a Systemair VSR unit via Modbus."""

    def __init__(self, host: str, port: int, slave_id: int, timeout: int = 5):
        """Initialize the Modbus client."""
        self._client = AsyncModbusTcpClient(host, port=port, timeout=timeout)
        self.slave_id = slave_id
        self._lock = asyncio.Lock()
        self._is_connected = False

    async def close(self):
        """Close the Modbus connection."""
        if self._is_connected:
            self._client.close()
            self._is_connected = False

    async def _ensure_connected(self):
        """Ensure the client is connected, establishing connection if needed."""
        if not self._is_connected:
            self._is_connected = await self._client.connect()
            if not self._is_connected:
                raise ModbusConnectionError("Could not connect to VSR unit")

    async def test_connection(self) -> bool:
        """Test the connection to the Modbus device."""
        async with self._lock:
            try:
                await self._ensure_connected()
                test_register_1based = parameter_map["REG_TC_SP"].register
                await self._client.read_holding_registers(
                    address=test_register_1based - 1, count=1, device_id=self.slave_id
                )
                return True
            except (ModbusException, ModbusConnectionError) as e:
                LOGGER.error("Failed to connect during test: %s", e)
                return False
            finally:
                await self.close()

    async def write_register(self, address_1based: int, value: int):
        """Write a single holding register. Expects a 1-based address."""
        async with self._lock:
            try:
                await self._ensure_connected()
                result = await self._client.write_register(
                    address=address_1based - 1, value=value, device_id=self.slave_id
                )
                if result.isError():
                    raise ModbusConnectionError(
                        f"Error writing to register {address_1based}: {result}"
                    )
                LOGGER.debug(f"Successfully wrote {value} to register {address_1based}")
            except (ModbusException, ModbusConnectionError) as e:
                LOGGER.error("Modbus write error: %s", e)
                await self.close()
                raise

    async def get_all_data(self) -> dict[str, Any]:
        """Read all required registers using block reads with retry logic for stability."""
        read_blocks = [
            (1001, 62), (1101, 80), (2001, 50), (2505, 1), (3002, 116),
            (4100, 1), (7005, 2), (12102, 40), (12306, 12), (12401, 2),
            (12544, 1), (14001, 4), (14101, 5), (14201, 2), (14381, 1),
            (15016, 125), (15141, 125), (15266, 125), (15391, 125),
            (15516, 125), (15641, 125), (15766, 125), (15891, 13),
        ]

        all_registers = {}
        max_retries = 3
        retry_delay = 0.25

        async with self._lock:
            try:
                await self._ensure_connected()
                for start_addr_1based, count in read_blocks:
                    for attempt in range(max_retries):
                        result = await self._client.read_holding_registers(
                            address=start_addr_1based - 1, count=count, device_id=self.slave_id
                        )
                        if result.isError():
                            if result.exception_code == 6 and attempt < max_retries - 1:
                                LOGGER.debug(f"Device busy on block starting at {start_addr_1based}, retrying...")
                                await asyncio.sleep(retry_delay)
                                continue
                            raise ModbusConnectionError(f"Block {start_addr_1based} read error: {result}")

                        for i, reg_val in enumerate(result.registers):
                            key = str(start_addr_1based - 1 + i)
                            all_registers[key] = reg_val
                        break
                    else:
                        raise ModbusConnectionError(f"Failed to read block {start_addr_1based} after retries.")
                    await asyncio.sleep(0.05)
            except (ModbusException, ModbusConnectionError) as e:
                LOGGER.error("Modbus read error during full update: %s", e)
                await self.close()
                raise

        return all_registers
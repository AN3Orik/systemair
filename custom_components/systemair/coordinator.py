"""DataUpdateCoordinator for Systemair."""

from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING, Any

from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import ModbusConnectionError, SystemairVSRModbusClient
from .const import DOMAIN, LOGGER
from .modbus import IntegerType, parameter_map

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from .data import SystemairConfigEntry
    from .modbus import ModbusParameter


class InvalidBooleanValueError(HomeAssistantError):
    """Exception raised for invalid boolean values."""

    def __init__(self) -> None:
        """Initialize."""
        super().__init__("Value must be a boolean")


class SystemairDataUpdateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Class to manage fetching data from the API."""

    config_entry: SystemairConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        client: SystemairVSRModbusClient,
    ) -> None:
        """Initialize."""
        self.client = client
        super().__init__(
            hass=hass,
            logger=LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=10),
        )

    def get_modbus_data(self, register: ModbusParameter) -> float | bool:
        """Get the data for a Modbus register."""
        if self.data is None:
            return 0

        value = self.data.get(str(register.register - 1))

        if value is None:
            return 0
        if register.boolean:
            return value != 0
        value = int(value)

        if register.combine_with_32_bit:
            high = self.data.get(str(register.combine_with_32_bit - 1))
            if high is None:
                return 0
            value += int(high) << 16

        if register.sig == IntegerType.INT and value > (1 << 15) - 1:
            value = -(65536 - value)
        return value / (register.scale_factor or 1)

    async def set_modbus_data(self, register: ModbusParameter, value: Any) -> None:
        """Set the data for a Modbus register."""
        if register.boolean:
            if not isinstance(value, bool):
                raise InvalidBooleanValueError
            value_to_write = 1 if value else 0
        else:
            value_to_write = int(value * (register.scale_factor or 1))
            if register.min_value is not None and value_to_write < register.min_value:
                value_to_write = register.min_value
            if register.max_value is not None and value_to_write > register.max_value:
                value_to_write = register.max_value

        try:
            await self.client.write_register(register.register, value_to_write)
            await self.async_request_refresh()
        except ModbusConnectionError as exc:
            raise UpdateFailed(f"Failed to write to register {register.register}: {exc}") from exc

    async def _async_update_data(self) -> dict[str, Any]:
        """Update data via library."""
        try:
            return await self.client.get_all_data()
        except ModbusConnectionError as exception:
            raise UpdateFailed(exception) from exception
"""DataUpdateCoordinator for Systemair."""

from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING, Any

from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import (
    ModbusConnectionError,
    SystemairApiClientError,
    SystemairClientBase,
    SystemairWebApiClient,
)
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
        client: SystemairClientBase,
        config_entry: SystemairConfigEntry,
    ) -> None:
        """Initialize."""
        self.client = client
        self.config_entry = config_entry
        self._is_webapi = isinstance(client, SystemairWebApiClient)

        self.modbus_parameters: list[ModbusParameter] = []

        super().__init__(
            hass=hass,
            logger=LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=10),
        )

    def register_modbus_parameters(self, modbus_parameter: ModbusParameter) -> None:
        """Register a Modbus parameter to be updated (for WebAPI)."""
        if not self._is_webapi:
            return

        if modbus_parameter not in self.modbus_parameters:
            self.modbus_parameters.append(modbus_parameter)

        if modbus_parameter.combine_with_32_bit:
            combine_with = next(
                (param for param in parameter_map.values() if param.register == modbus_parameter.combine_with_32_bit),
                None,
            )

            if combine_with and combine_with not in self.modbus_parameters:
                self.modbus_parameters.append(combine_with)

    def get_modbus_data(self, register: ModbusParameter) -> float | bool:
        """Get the data for a Modbus register."""
        if self._is_webapi:
            self.register_modbus_parameters(register)

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
        except (ModbusConnectionError, SystemairApiClientError) as exc:
            msg = f"Failed to write to register {register.register}: {exc}"
            raise UpdateFailed(msg) from exc

    async def async_set_modbus_data_32bit(self, register: ModbusParameter, value: int) -> None:
        """Set the data for a 32-bit Modbus register."""
        try:
            await self.client.write_registers_32bit(register.register, value)
            await self.async_request_refresh()
        except (ModbusConnectionError, SystemairApiClientError) as exc:
            msg = f"Failed to write to 32-bit register starting at {register.register}: {exc}"
            raise UpdateFailed(msg) from exc

    async def async_setup_webapi(self) -> None:
        """Set up coordinator for WebAPI (get device info)."""
        if not self._is_webapi:
            return

        try:
            menu = await self.client.async_get_endpoint("menu")
            unit_version = await self.client.async_get_endpoint("unit_version")
            self.config_entry.runtime_data.mac_address = menu["mac"]
            self.config_entry.runtime_data.serial_number = unit_version["System Serial Number"]
            self.config_entry.runtime_data.mb_hw_version = unit_version["MB HW version"]
            self.config_entry.runtime_data.mb_model = unit_version["MB Model"]
            self.config_entry.runtime_data.mb_sw_version = unit_version["MB SW version"]
            self.config_entry.runtime_data.iam_sw_version = unit_version["IAM SW version"]

            # Set configuration URL for web interface access
            if hasattr(self.client, "address"):
                self.config_entry.runtime_data.configuration_url = f"http://{self.client.address}"

            # Required for setup of climate entity
            self.register_modbus_parameters(parameter_map["REG_FUNCTION_ACTIVE_HEATER"])
            self.register_modbus_parameters(parameter_map["REG_FUNCTION_ACTIVE_COOLER"])
        except SystemairApiClientError as exception:
            LOGGER.error("Failed to setup WebAPI: %s", exception)

    async def _async_update_data(self) -> dict[str, Any]:
        """Update data via library."""
        try:
            if self._is_webapi:
                if self.modbus_parameters:
                    return await self.client.async_get_data(self.modbus_parameters)
                return await self.client.get_all_data()
            return await self.client.get_all_data()
        except (ModbusConnectionError, SystemairApiClientError) as exception:
            raise UpdateFailed(exception) from exception

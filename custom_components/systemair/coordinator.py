"""DataUpdateCoordinator for Systemair."""

from __future__ import annotations

import asyncio
import time
from datetime import timedelta
from typing import TYPE_CHECKING, Any

from homeassistant.exceptions import ConfigEntryAuthFailed, HomeAssistantError
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import (
    ModbusConnectionError,
    SystemairApiClientError,
    SystemairAuthError,
    SystemairAuthExpiredError,
    SystemairAuthRequiredError,
    SystemairClientBase,
    SystemairWebApiClient,
)
from .const import (
    CONF_ENABLE_ALARM_DETAILS,
    CONF_ENABLE_ALARM_HISTORY,
    DEFAULT_ENABLE_ALARM_DETAILS,
    DEFAULT_ENABLE_ALARM_HISTORY,
    DOMAIN,
    LOGGER,
)
from .homesolution import SystemairHomeSolutionClient
from .homesolution_mapping import resolve_homesolution_value
from .modbus import IntegerType, parameter_map

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from .data import SystemairConfigEntry
    from .modbus import ModbusParameter

TRANSIENT_FAILURE_THRESHOLD = 3
POST_WRITE_REFRESH_COOLDOWN = 2.0


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
        update_interval_seconds: int = 60,
    ) -> None:
        """Initialize."""
        self.client = client
        self.config_entry = config_entry
        self._is_webapi = isinstance(client, SystemairWebApiClient)
        self._is_homesolution = isinstance(client, SystemairHomeSolutionClient)

        if self._is_homesolution:
            self.client.set_update_callback(self.async_set_updated_data_from_ws)

        self.modbus_parameters: list[ModbusParameter] = []
        self._consecutive_update_failures = 0
        self._last_write_refresh: float | None = None
        self._write_since_last_refresh = False
        self._trailing_refresh_handle: asyncio.TimerHandle | None = None
        self._trailing_refresh_task: asyncio.Task[None] | None = None

        super().__init__(
            hass=hass,
            logger=LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=update_interval_seconds),
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

    def get_modbus_data(self, register: ModbusParameter) -> float | bool | None:
        """Get the data for a Modbus register."""
        if self._is_webapi:
            self.register_modbus_parameters(register)

        if self.data is None:
            return None

        if self._is_homesolution:
            # HomeSolution Logic
            # The data stored in self.data is the VentilationUnit object if homesolution
            if isinstance(self.data, dict):
                # Fallback if for some reason it is a dict (should not happen with new logic)
                pass
            else:
                return resolve_homesolution_value(self.data, register)

        value = self.data.get(str(register.register - 1))

        if value is None:
            return None
        if register.boolean:
            return value != 0
        value = int(value)

        if register.combine_with_32_bit:
            high = self.data.get(str(register.combine_with_32_bit - 1))
            if high is None:
                return None
            value += int(high) << 16

        if register.sig == IntegerType.INT and value > (1 << 15) - 1:
            value = -(65536 - value)
        return value / (register.scale_factor or 1)

    def has_modbus_data(self, register: ModbusParameter) -> bool:
        """Return whether the active transport exposes a register value."""
        if not self._is_homesolution:
            return True
        return self.data is not None and not isinstance(self.data, dict) and resolve_homesolution_value(self.data, register) is not None

    def supports_modbus_data(self, register: ModbusParameter) -> bool:
        """Return whether the active transport declares a readable capability."""
        return not self._is_homesolution or self.client.supports_register(register)

    @property
    def homesolution_capabilities_complete(self) -> bool:
        """Return whether optional cloud entities can be filtered safely."""
        return self._is_homesolution and self.client.capabilities_discovered

    def get_raw_register(self, address_1based: int) -> Any | None:
        """Read an unscaled SAVE register address from the active transport."""
        if self.data is None:
            return None
        if self._is_homesolution and not isinstance(self.data, dict):
            return self.data.get_raw_modbus_register(address_1based)
        return self.data.get(str(address_1based - 1))

    def has_raw_register(self, address_1based: int) -> bool:
        """Return whether an unscaled SAVE address exists in current data."""
        return self.get_raw_register(address_1based) is not None

    def can_set_modbus_data(self, register: ModbusParameter) -> bool:
        """Return whether the active transport can write this register."""
        return not self._is_homesolution or self.client.can_write_register(register)

    def can_set_modbus_data_32bit(self, register: ModbusParameter) -> bool:
        """Return whether the active transport can write both halves of a value."""
        return not self._is_homesolution or self.client.can_write_registers_32bit(register)

    def _schedule_trailing_write_refresh(self, delay: float) -> None:
        """Schedule a single coalesced refresh after the write cooldown expires."""
        if getattr(self, "_trailing_refresh_handle", None) is not None:
            return

        loop = asyncio.get_running_loop()

        def _trigger_refresh() -> None:
            self._trailing_refresh_handle = None
            task_coro = self._async_run_trailing_write_refresh()
            hass = getattr(self, "hass", None)
            if hass is not None and hasattr(hass, "async_create_task"):
                self._trailing_refresh_task = hass.async_create_task(task_coro)
            else:
                self._trailing_refresh_task = loop.create_task(task_coro)

        self._trailing_refresh_handle = loop.call_later(delay, _trigger_refresh)

    async def _async_run_trailing_write_refresh(self) -> None:
        """Execute a trailing refresh queued during the write cooldown."""
        if not getattr(self, "_write_since_last_refresh", False):
            return
        self._write_since_last_refresh = False
        self._last_write_refresh = time.monotonic()
        await self.async_request_refresh()

    async def async_refresh_after_write(self) -> None:
        """Publish cloud readback locally or refresh the active local transport."""
        if self._is_homesolution:
            if self.client.unit is not None:
                self.async_set_updated_data(self.client.unit)
            return
        now = time.monotonic()
        last_refresh = getattr(self, "_last_write_refresh", None)
        if last_refresh is not None and (now - last_refresh) < POST_WRITE_REFRESH_COOLDOWN:
            if getattr(self, "_write_since_last_refresh", False):
                remaining = max(0.0, POST_WRITE_REFRESH_COOLDOWN - (now - last_refresh))
                self._schedule_trailing_write_refresh(remaining)
            return
        existing_handle = getattr(self, "_trailing_refresh_handle", None)
        if existing_handle is not None:
            existing_handle.cancel()
            self._trailing_refresh_handle = None
        self._write_since_last_refresh = False
        self._last_write_refresh = now
        await self.async_request_refresh()

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
            if isinstance(getattr(self, "data", None), dict):
                self.data[str(register.register - 1)] = value_to_write
                if hasattr(self, "async_update_listeners"):
                    self.async_update_listeners()
            self._write_since_last_refresh = True
            await self.async_refresh_after_write()
        except (SystemairAuthError, SystemairAuthExpiredError, SystemairAuthRequiredError) as exc:
            raise ConfigEntryAuthFailed(str(exc)) from exc
        except (ModbusConnectionError, SystemairApiClientError) as exc:
            msg = f"Failed to write to register {register.register}: {exc}"
            raise UpdateFailed(msg) from exc

    async def async_set_modbus_data_32bit(self, register: ModbusParameter, value: int) -> None:
        """Set the data for a 32-bit Modbus register."""
        try:
            await self.client.write_registers_32bit(register.register, value)
            if isinstance(getattr(self, "data", None), dict):
                self.data[str(register.register - 1)] = value & 0xFFFF
                self.data[str(register.register)] = (value >> 16) & 0xFFFF
                if hasattr(self, "async_update_listeners"):
                    self.async_update_listeners()
            self._write_since_last_refresh = True
            await self.async_refresh_after_write()
        except (SystemairAuthError, SystemairAuthExpiredError, SystemairAuthRequiredError) as exc:
            raise ConfigEntryAuthFailed(str(exc)) from exc
        except (ModbusConnectionError, SystemairApiClientError) as exc:
            msg = f"Failed to write to 32-bit register starting at {register.register}: {exc}"
            raise UpdateFailed(msg) from exc

    def async_set_updated_data_from_ws(self) -> None:
        """Update data from WebSocket callback."""
        if self.client.unit:
            self.hass.loop.call_soon_threadsafe(self.async_set_updated_data, self.client.unit)

    async def async_setup_webapi(self) -> None:
        """Set up coordinator for WebAPI (get device info)."""
        if not self._is_webapi:
            return

        try:
            menu = await self.client.async_get_endpoint("menu")
            unit_version = await self.client.async_get_endpoint("unit_version")
            self.config_entry.runtime_data.mac_address = menu.get("mac", "Unknown")
            self.config_entry.runtime_data.serial_number = unit_version.get("System Serial Number", "Unknown")
            self.config_entry.runtime_data.mb_hw_version = unit_version.get("MB HW version", "Unknown")
            self.config_entry.runtime_data.mb_model = unit_version.get("MB Model", "Unknown")
            self.config_entry.runtime_data.mb_sw_version = unit_version.get("MB SW version", "Unknown")
            self.config_entry.runtime_data.iam_sw_version = unit_version.get("IAM SW version", "Unknown")

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
            enable_alarm_details = self.config_entry.options.get(CONF_ENABLE_ALARM_DETAILS, DEFAULT_ENABLE_ALARM_DETAILS)
            enable_alarm_history = self.config_entry.options.get(CONF_ENABLE_ALARM_HISTORY, DEFAULT_ENABLE_ALARM_HISTORY)
            if self._is_webapi and self.modbus_parameters:
                new_data = await self.client.async_get_data(self.modbus_parameters)
            else:
                # For HomeSolution, get_all_data returns the VentilationUnit object
                # For others, it returns a dict of registers
                new_data = await self.client.get_all_data(
                    enable_alarm_details=enable_alarm_details,
                    enable_alarm_history=enable_alarm_history,
                )
        except (SystemairAuthError, SystemairAuthExpiredError, SystemairAuthRequiredError) as exception:
            raise ConfigEntryAuthFailed(str(exception)) from exception
        except (ModbusConnectionError, SystemairApiClientError) as exception:
            failures = getattr(self, "_consecutive_update_failures", 0) + 1
            self._consecutive_update_failures = failures
            current_data = getattr(self, "data", None)
            if current_data is not None and failures <= TRANSIENT_FAILURE_THRESHOLD:
                LOGGER.warning(
                    "Transient error fetching %s data (%d/%d); keeping cached state: %s",
                    DOMAIN,
                    failures,
                    TRANSIENT_FAILURE_THRESHOLD,
                    exception,
                )
                return current_data
            raise UpdateFailed(exception) from exception

        current_data = getattr(self, "data", None)
        merged_data = {**current_data, **new_data} if isinstance(current_data, dict) and isinstance(new_data, dict) else new_data
        partial_error = getattr(self.client, "last_read_error", None) if self._is_webapi else None

        if partial_error is not None:
            failures = getattr(self, "_consecutive_update_failures", 0) + 1
            self._consecutive_update_failures = failures
            if current_data is not None and failures <= TRANSIENT_FAILURE_THRESHOLD:
                LOGGER.warning(
                    "Partial error fetching %s data (%d/%d); keeping cached state for failed chunks: %s",
                    DOMAIN,
                    failures,
                    TRANSIENT_FAILURE_THRESHOLD,
                    partial_error,
                )
                return merged_data
            if isinstance(merged_data, dict):
                self.data = merged_data
            raise UpdateFailed(partial_error) from partial_error

        self._consecutive_update_failures = 0
        return merged_data

"""DataUpdateCoordinator for Systemair."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING, Any

from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import (
    ModbusConnectionError,
    SystemairApiClientCommunicationError,
    SystemairApiClientError,
    SystemairApiClientTemporaryUnavailableError,
    SystemairClientBase,
    SystemairWebApiClient,
)
from .const import (
    CONF_CONFIG_POLL_INTERVAL,
    CONF_STATUS_OFF_SKIP_FACTOR,
    CONF_STATUS_POLL_INTERVAL,
    DEFAULT_STATUS_OFF_SKIP_FACTOR,
    DEFAULT_STATUS_POLL_INTERVAL,
    DEFAULT_WEB_API_CONFIG_POLL_INTERVAL,
    DOMAIN,
    LOGGER,
)
from .modbus import IntegerType, RegisterType, parameter_map

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

        # Separate parameter sets for status (Input) vs config (Holding)
        self._status_parameters: list[ModbusParameter] = []
        self._config_parameters: list[ModbusParameter] = []
        self._last_config_poll: datetime | None = None
        self._force_next_config_poll: bool = False
        # Adaptive offline cooldown handling for WebAPI transient outages
        self._offline_until: datetime | None = None
        self._offline_cooldown_sec: int = 0
        self._offline_cooldown_max_sec: int = 900  # cap at 15 minutes
        # Duty cycling: when fans are off, skip status polls to reduce load
        self._status_off_skip_factor: int = max(
            1, int(self.config_entry.options.get(CONF_STATUS_OFF_SKIP_FACTOR, DEFAULT_STATUS_OFF_SKIP_FACTOR))
        )
        self._status_off_skip_counter: int = 0
        # Config (Holding) poll interval, can be overridden via options
        self._config_poll_interval_sec: int = int(
            self.config_entry.options.get(CONF_CONFIG_POLL_INTERVAL, DEFAULT_WEB_API_CONFIG_POLL_INTERVAL)
        )

        super().__init__(
            hass=hass,
            logger=LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=int(self.config_entry.options.get(CONF_STATUS_POLL_INTERVAL, DEFAULT_STATUS_POLL_INTERVAL))),
        )

    def register_modbus_parameters(self, modbus_parameter: ModbusParameter) -> None:
        """Register a Modbus parameter to be updated (for WebAPI)."""
        if not self._is_webapi:
            return

        # Choose target list by register type
        target_list = self._status_parameters if modbus_parameter.reg_type == RegisterType.Input else self._config_parameters

        if modbus_parameter not in target_list:
            target_list.append(modbus_parameter)

        # Ensure paired 32-bit register is also tracked in the same group
        if modbus_parameter.combine_with_32_bit:
            combine_with = next(
                (param for param in parameter_map.values() if param.register == modbus_parameter.combine_with_32_bit),
                None,
            )

            if combine_with and combine_with not in target_list:
                target_list.append(combine_with)

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
            # Ensure we refresh config values promptly after a write
            self._force_next_config_poll = True
            await self.async_request_refresh()
        except (ModbusConnectionError, SystemairApiClientError) as exc:
            msg = f"Failed to write to register {register.register}: {exc}"
            raise UpdateFailed(msg) from exc

    async def async_set_modbus_data_32bit(self, register: ModbusParameter, value: int) -> None:
        """Set the data for a 32-bit Modbus register."""
        try:
            await self.client.write_registers_32bit(register.register, value)
            # Ensure we refresh config values promptly after a write
            self._force_next_config_poll = True
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
            if not self._is_webapi:
                return await self.client.get_all_data()

            # For WebAPI, always poll status parameters; poll config less frequently
            merged: dict[str, Any] = dict(self.data or {})

            # If nothing registered yet, fall back to full read once
            if not self._status_parameters and not self._config_parameters:
                return await self.client.get_all_data()

            now = datetime.now(UTC)
            merged = await self._maybe_poll_status(now, merged)

            return await self._maybe_poll_config(now, merged)

        except (ModbusConnectionError, SystemairApiClientError) as exception:
            raise UpdateFailed(exception) from exception

    async def _maybe_poll_status(self, now: datetime, merged: dict[str, Any]) -> dict[str, Any]:
        skip_status = self._offline_until is not None and now < self._offline_until
        fans_key = str(parameter_map["REG_SPEED_FANS_RUNNING"].register - 1)
        cached_fans_val = (self.data or {}).get(fans_key)
        fans_running_cached = True if cached_fans_val is None else bool(cached_fans_val)
        if fans_running_cached:
            self._status_off_skip_counter = 0

        if self._status_parameters and not skip_status:
            if not fans_running_cached and self._status_off_skip_factor > 1:
                if self._status_off_skip_counter < self._status_off_skip_factor - 1:
                    self._status_off_skip_counter += 1
                    LOGGER.debug(
                        "Fans off; skipping status poll %d/%d; serving cached.",
                        self._status_off_skip_counter,
                        self._status_off_skip_factor - 1,
                    )
                    return merged
                self._status_off_skip_counter = 0
            try:
                status_data = await self.client.async_get_data(self._status_parameters)
                merged.update(status_data)
                self._offline_until = None
                self._offline_cooldown_sec = 0
            except (SystemairApiClientTemporaryUnavailableError, SystemairApiClientCommunicationError) as exc:
                self._offline_cooldown_sec = max(30, self._offline_cooldown_sec * 2 or 30)
                self._offline_cooldown_sec = min(self._offline_cooldown_sec, self._offline_cooldown_max_sec)
                self._offline_until = now + timedelta(seconds=self._offline_cooldown_sec)
                LOGGER.warning(
                    "Status poll temporarily unavailable (%s). Cooldown %ds; serving cached.",
                    exc,
                    self._offline_cooldown_sec,
                )
            except (ModbusConnectionError, SystemairApiClientError) as exc:
                raise UpdateFailed(exc) from exc
        elif skip_status:
            LOGGER.debug("Skipping status poll during offline cooldown; serving cached data.")
        return merged

    async def _maybe_poll_config(self, now: datetime, merged: dict[str, Any]) -> dict[str, Any]:
        do_config_poll = False
        if self._force_next_config_poll or self._last_config_poll is None:
            do_config_poll = True
        else:
            elapsed = (now - self._last_config_poll).total_seconds()
            do_config_poll = elapsed >= self._config_poll_interval_sec

        if do_config_poll and self._config_parameters and not (self._offline_until and now < self._offline_until):
            try:
                config_data = await self.client.async_get_data(self._config_parameters)
                merged.update(config_data)
                self._last_config_poll = now
            except (ModbusConnectionError, SystemairApiClientError) as exc:
                LOGGER.warning("Config poll failed: %s", exc)
            finally:
                self._force_next_config_poll = False
        elif do_config_poll and (self._offline_until and now < self._offline_until):
            LOGGER.debug("Skipping config poll during offline cooldown.")
        return merged

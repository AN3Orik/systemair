"""Systemair HVAC integration."""

import asyncio.exceptions
from typing import TYPE_CHECKING, Any, ClassVar

from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
    HVACAction,
    HVACMode,
)
from homeassistant.components.climate.const import (
    FAN_HIGH,
    FAN_LOW,
    FAN_MEDIUM,
    FAN_OFF,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_TEMPERATURE, PRECISION_WHOLE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddEntitiesCallback

if TYPE_CHECKING:
    from .coordinator import SystemairDataUpdateCoordinator

from .const import (
    MAX_TEMP,
    MIN_TEMP,
    PRESET_MODE_AUTO,
    PRESET_MODE_AWAY,
    PRESET_MODE_CDI1,
    PRESET_MODE_CDI2,
    PRESET_MODE_CDI3,
    PRESET_MODE_COOKER_HOOD,
    PRESET_MODE_CROWDED,
    PRESET_MODE_FIREPLACE,
    PRESET_MODE_HOLIDAY,
    PRESET_MODE_MANUAL,
    PRESET_MODE_PRESSURE_GUARD,
    PRESET_MODE_REFRESH,
    PRESET_MODE_VACUUM_CLEANER,
)
from .coordinator import SystemairDataUpdateCoordinator
from .entity import SystemairEntity
from .fan_state import MANUAL_USER_MODE, FanState, resolve_fan_state
from .modbus import parameter_map
from .profiles import DEVICE_PROFILE_LEGACY_D24810

PRESET_MODE_TO_VALUE_MAP = {
    PRESET_MODE_AUTO: 1,
    PRESET_MODE_MANUAL: 2,
    PRESET_MODE_CROWDED: 3,
    PRESET_MODE_REFRESH: 4,
    PRESET_MODE_FIREPLACE: 5,
    PRESET_MODE_AWAY: 6,
    PRESET_MODE_HOLIDAY: 7,
    PRESET_MODE_COOKER_HOOD: 8,
    PRESET_MODE_VACUUM_CLEANER: 9,
    PRESET_MODE_CDI1: 10,
    PRESET_MODE_CDI2: 11,
    PRESET_MODE_CDI3: 12,
    PRESET_MODE_PRESSURE_GUARD: 13,
}

VALUE_TO_PRESET_MODE_MAP = {value - 1: key for key, value in PRESET_MODE_TO_VALUE_MAP.items()}

FAN_MODE_TO_VALUE_MAP = {
    FAN_OFF: 0,
    FAN_LOW: 2,
    FAN_MEDIUM: 3,
    FAN_HIGH: 4,
}


async def async_setup_entry(
    _hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Systemair unit."""
    if config_entry.runtime_data.profile.profile_id == DEVICE_PROFILE_LEGACY_D24810:
        async_add_entities([SystemairD24810ClimateEntity(config_entry.runtime_data.coordinator)])
        return

    async_add_entities([SystemairClimateEntity(config_entry.runtime_data.coordinator)])


class SystemairClimateEntity(SystemairEntity, ClimateEntity):
    """Systemair air handling unit."""

    _attr_has_entity_name = True
    _enable_turn_on_off_backwards_compatibility = False

    _attr_preset_modes: ClassVar[list[str]] = [
        PRESET_MODE_AUTO,
        PRESET_MODE_MANUAL,
        PRESET_MODE_CROWDED,
        PRESET_MODE_REFRESH,
        PRESET_MODE_FIREPLACE,
        PRESET_MODE_AWAY,
        PRESET_MODE_HOLIDAY,
    ]

    _attr_fan_modes: ClassVar[list[str]] = [
        FAN_OFF,
        FAN_LOW,
        FAN_MEDIUM,
        FAN_HIGH,
    ]

    _attr_supported_features = (
        ClimateEntityFeature.PRESET_MODE
        | ClimateEntityFeature.TARGET_TEMPERATURE
        | ClimateEntityFeature.FAN_MODE
        | ClimateEntityFeature.TURN_ON
        | ClimateEntityFeature.TURN_OFF
    )

    _attr_target_temperature_step = PRECISION_WHOLE
    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_max_temp = MAX_TEMP
    _attr_min_temp = MIN_TEMP

    def __init__(self, coordinator: SystemairDataUpdateCoordinator) -> None:
        """Initialize the Systemair unit."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}-climate"
        self._attr_translation_key = "saveconnect"

        self._attr_hvac_modes = [HVACMode.OFF, HVACMode.FAN_ONLY]

        heater = self.coordinator.get_modbus_data(parameter_map["REG_FUNCTION_ACTIVE_HEATER"])
        cooler = self.coordinator.get_modbus_data(parameter_map["REG_FUNCTION_ACTIVE_COOLER"])

        if heater:
            self._attr_hvac_modes.append(HVACMode.HEAT)
        if cooler:
            self._attr_hvac_modes.append(HVACMode.COOL)

    @property
    def available(self) -> bool:
        """Return whether HomeSolution exposes all core climate controls."""
        if not self._is_homesolution:
            return super().available
        core_readable = (
            parameter_map["REG_USERMODE_MODE"],
            parameter_map["REG_TC_SP"],
        )
        writable = (
            parameter_map["REG_USERMODE_HMI_CHANGE_REQUEST"],
            parameter_map["REG_USERMODE_MANUAL_AIRFLOW_LEVEL_SAF"],
            parameter_map["REG_TC_SP"],
        )
        if (
            not super().available
            or not all(self.coordinator.has_modbus_data(register) for register in core_readable)
            or not all(self.coordinator.can_set_modbus_data(register) for register in writable)
        ):
            return False

        actual = parameter_map["REG_SPEED_INDICATION_APP"]
        if self.coordinator.has_modbus_data(actual):
            return True

        active_mode = self.coordinator.get_modbus_data(parameter_map["REG_USERMODE_MODE"])
        manual = parameter_map["REG_USERMODE_MANUAL_AIRFLOW_LEVEL_SAF"]
        return active_mode == MANUAL_USER_MODE and self.coordinator.has_modbus_data(manual)

    def _fan_state(self) -> FanState:
        """Resolve actual fan state with transport-appropriate freshness."""
        fan_outputs = None
        if not self._is_homesolution:
            fan_outputs = (
                self.coordinator.get_modbus_data(parameter_map["REG_OUTPUT_SAF"]),
                self.coordinator.get_modbus_data(parameter_map["REG_OUTPUT_EAF"]),
            )
        return resolve_fan_state(
            actual_level=self.coordinator.get_modbus_data(parameter_map["REG_SPEED_INDICATION_APP"]),
            active_user_mode=self.coordinator.get_modbus_data(parameter_map["REG_USERMODE_MODE"]),
            manual_level=self.coordinator.get_modbus_data(parameter_map["REG_USERMODE_MANUAL_AIRFLOW_LEVEL_SAF"]),
            fan_outputs=fan_outputs,
        )

    @property
    def hvac_mode(self) -> HVACMode:
        """Return hvac operation ie. heat, cool mode."""
        if self._fan_state().running is False:
            return HVACMode.OFF

        heater = self.coordinator.get_modbus_data(parameter_map["REG_FUNCTION_ACTIVE_HEATER"])
        cooler = self.coordinator.get_modbus_data(parameter_map["REG_FUNCTION_ACTIVE_COOLER"])

        if heater and cooler:
            return HVACMode.HEAT_COOL
        if heater:
            return HVACMode.HEAT
        if cooler:
            return HVACMode.COOL

        return HVACMode.FAN_ONLY

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set new target hvac mode."""
        if hvac_mode == HVACMode.OFF:
            await self.async_turn_off()
        else:
            await self.async_turn_on()

    async def async_turn_on(self, **_kwargs: Any) -> None:
        """Turn the entity on."""
        try:
            await self.coordinator.set_modbus_data(parameter_map["REG_USERMODE_MANUAL_AIRFLOW_LEVEL_SAF"], 2)
        except (asyncio.exceptions.TimeoutError, ConnectionError) as exc:
            raise HomeAssistantError from exc
        finally:
            await self.coordinator.async_refresh_after_write()

    async def async_turn_off(self, **_kwargs: Any) -> None:
        """Turn the entity off."""
        try:
            await self.coordinator.set_modbus_data(parameter_map["REG_USERMODE_MANUAL_AIRFLOW_LEVEL_SAF"], 0)
        except (asyncio.exceptions.TimeoutError, ConnectionError) as exc:
            raise HomeAssistantError from exc
        finally:
            await self.coordinator.async_refresh_after_write()

    @property
    def hvac_action(self) -> HVACAction | None:
        """Return current HVAC action."""
        if self._fan_state().running is False:
            return HVACAction.OFF

        heater = self.coordinator.get_modbus_data(parameter_map["REG_OUTPUT_TRIAC"])
        cooler = self.coordinator.get_modbus_data(parameter_map["REG_OUTPUT_Y3_DIGITAL"])

        if heater:
            return HVACAction.HEATING
        if cooler:
            return HVACAction.COOLING

        return HVACAction.FAN

    @property
    def current_humidity(self) -> float | None:
        """Return the current humidity."""
        return self.coordinator.get_modbus_data(parameter_map["REG_SENSOR_RHS_PDM"])

    @property
    def current_temperature(self) -> float:
        """Return the current temperature."""
        return self.coordinator.get_modbus_data(parameter_map["REG_SENSOR_SAT"])

    @property
    def target_temperature(self) -> float:
        """Return the temperature we try to reach."""
        return self.coordinator.get_modbus_data(parameter_map["REG_TC_SP"])

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set new target temperature."""
        if (temperature := kwargs.get(ATTR_TEMPERATURE)) is None:
            return

        try:
            await self.coordinator.set_modbus_data(parameter_map["REG_TC_SP"], temperature)
        except (asyncio.exceptions.TimeoutError, ConnectionError) as exc:
            raise HomeAssistantError from exc
        finally:
            await self.coordinator.async_refresh_after_write()

    @property
    def preset_mode(self) -> str | None:
        """Return the current preset mode."""
        mode = self.coordinator.get_modbus_data(parameter_map["REG_USERMODE_MODE"])
        if mode is None:
            return None
        return VALUE_TO_PRESET_MODE_MAP.get(int(mode), PRESET_MODE_MANUAL)

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set new preset mode."""
        ventilation_mode = PRESET_MODE_TO_VALUE_MAP[preset_mode]

        try:
            await self.coordinator.set_modbus_data(parameter_map["REG_USERMODE_HMI_CHANGE_REQUEST"], ventilation_mode)
        except (asyncio.exceptions.TimeoutError, ConnectionError) as exc:
            raise HomeAssistantError from exc
        finally:
            await self.coordinator.async_refresh_after_write()

    @property
    def fan_mode(self) -> str | None:
        """Return the current fan mode."""
        return self._fan_state().fan_mode

    async def async_set_fan_mode(self, fan_mode: str) -> None:
        """Set new target fan mode."""
        mode = FAN_MODE_TO_VALUE_MAP[fan_mode]
        try:
            await self.coordinator.set_modbus_data(parameter_map["REG_USERMODE_MANUAL_AIRFLOW_LEVEL_SAF"], mode)
        except (asyncio.exceptions.TimeoutError, ConnectionError) as exc:
            raise HomeAssistantError from exc
        finally:
            await self.coordinator.async_refresh_after_write()


class SystemairD24810ClimateEntity(SystemairEntity, ClimateEntity):
    """Climate entity backed by D24810 registers."""

    _attr_has_entity_name = True
    _enable_turn_on_off_backwards_compatibility = False
    _attr_name = None
    _attr_fan_modes: ClassVar[list[str]] = [FAN_OFF, FAN_LOW, FAN_MEDIUM, FAN_HIGH, PRESET_MODE_AUTO]
    _attr_hvac_modes: ClassVar[list[HVACMode]] = [HVACMode.OFF, HVACMode.FAN_ONLY]
    _attr_supported_features = ClimateEntityFeature.FAN_MODE
    _attr_temperature_unit = UnitOfTemperature.CELSIUS

    _FAN_VALUE_TO_MODE: ClassVar[dict[int, str]] = {
        0: FAN_OFF,
        1: FAN_LOW,
        2: FAN_MEDIUM,
        3: FAN_HIGH,
        4: PRESET_MODE_AUTO,
    }
    _FAN_MODE_TO_VALUE: ClassVar[dict[str, int]] = {mode: value for value, mode in _FAN_VALUE_TO_MODE.items()}

    def __init__(self, coordinator: SystemairDataUpdateCoordinator) -> None:
        """Initialize the D24810 climate entity."""
        super().__init__(coordinator)
        self._attr_translation_key = "saveconnect"
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}-climate"

    def _register_value(self, key: str) -> int | float | None:
        """Read a climate register by logical D24810 climate key."""
        profile = self.coordinator.config_entry.runtime_data.profile
        register = profile.registry[profile.climate_registers[key]]
        return self.coordinator.get_modbus_data(register)

    @property
    def hvac_mode(self) -> HVACMode:
        """Return fan-only or off mode based on D24810 fan level."""
        return HVACMode.OFF if self.fan_mode == FAN_OFF else HVACMode.FAN_ONLY

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Map HVAC mode changes to the D24810 fan mode register."""
        if hvac_mode == HVACMode.OFF:
            await self.async_set_fan_mode(FAN_OFF)
            return

        if self.fan_mode in (None, FAN_OFF):
            await self.async_set_fan_mode(FAN_LOW)

    @property
    def current_temperature(self) -> float | None:
        """Return supply air temperature."""
        value = self._register_value("current_temperature")
        return None if value is None else float(value)

    @property
    def target_temperature(self) -> float | None:
        """Return the current D24810 temperature set point."""
        value = self._register_value("target_temperature")
        return None if value is None else float(value)

    @property
    def fan_mode(self) -> str | None:
        """Return the current D24810 fan speed level."""
        value = self._register_value("fan_mode")
        return None if value is None else self._FAN_VALUE_TO_MODE.get(int(value))

    async def async_set_fan_mode(self, fan_mode: str) -> None:
        """Set the D24810 fan speed level."""
        value = self._FAN_MODE_TO_VALUE.get(fan_mode)
        if value is None:
            msg = "Invalid fan mode"
            raise HomeAssistantError(msg)

        profile = self.coordinator.config_entry.runtime_data.profile
        register = profile.registry[profile.climate_registers["fan_mode"]]
        try:
            await self.coordinator.set_modbus_data(register, value)
        except (asyncio.exceptions.TimeoutError, ConnectionError) as exc:
            raise HomeAssistantError from exc
        finally:
            await self.coordinator.async_refresh_after_write()

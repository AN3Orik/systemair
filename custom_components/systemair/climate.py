"""Systemair HVAC integration."""

import asyncio.exceptions
from typing import Any, ClassVar

from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
    HVACAction,
    HVACMode,
)
from homeassistant.components.climate.const import (
    FAN_OFF,
    FAN_HIGH,
    FAN_LOW,
    FAN_MEDIUM,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_TEMPERATURE, PRECISION_WHOLE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddEntitiesCallback

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
from .modbus import parameter_map

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
    FAN_LOW: 2,
    FAN_MEDIUM: 3,
    FAN_HIGH: 4,
}

VALUE_TO_FAN_MODE_MAP = {value: key for key, value in FAN_MODE_TO_VALUE_MAP.items()}


async def async_setup_entry(
    _hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Systemair unit."""
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
    def hvac_mode(self) -> HVACMode:
        """Return hvac operation ie. heat, cool mode."""
        # Reflect actual fan state using the "fans running" status,
        # since schedules/auto can override manual airflow register.
        fans_running = self.coordinator.get_modbus_data(parameter_map["REG_SPEED_FANS_RUNNING"])  # bool
        if not fans_running:
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
            await self.coordinator.async_refresh()

    async def async_turn_off(self, **_kwargs: Any) -> None:
        """Turn the entity off."""
        try:
            await self.coordinator.set_modbus_data(parameter_map["REG_USERMODE_MANUAL_AIRFLOW_LEVEL_SAF"], 0)
        except (asyncio.exceptions.TimeoutError, ConnectionError) as exc:
            raise HomeAssistantError from exc
        finally:
            await self.coordinator.async_refresh()

    @property
    def hvac_action(self) -> HVACAction | None:
        """Return current HVAC action."""
        if self.hvac_mode == HVACMode.OFF:
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
            await self.coordinator.async_refresh()

    @property
    def preset_mode(self) -> str | None:
        """Return the current preset mode."""
        mode = self.coordinator.get_modbus_data(parameter_map["REG_USERMODE_MODE"])
        return VALUE_TO_PRESET_MODE_MAP.get(int(mode), PRESET_MODE_MANUAL)

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set new preset mode."""
        ventilation_mode = PRESET_MODE_TO_VALUE_MAP[preset_mode]

        try:
            await self.coordinator.set_modbus_data(parameter_map["REG_USERMODE_HMI_CHANGE_REQUEST"], ventilation_mode)
        except (asyncio.exceptions.TimeoutError, ConnectionError) as exc:
            raise HomeAssistantError from exc

    @property
    def fan_mode(self) -> str | None:
        """Return the current fan mode."""
        # Determine airflow level for the active preset to mirror actual behavior
        preset = self.preset_mode

        # If fans are not running at all, expose Off
        fans_running = self.coordinator.get_modbus_data(parameter_map["REG_SPEED_FANS_RUNNING"])  # bool
        if not fans_running:
            return FAN_OFF

        # Special handling for Auto: use demand-control fan speed to infer Low/Medium/High
        if preset == PRESET_MODE_AUTO:
            # When schedules/demand are active, map current DEMC speed to a coarse level
            # REG_DEMC_FAN_SPEED is a raw speed indicator; normalize and bucketize
            try:
                demc_speed = float(self.coordinator.get_modbus_data(parameter_map["REG_DEMC_FAN_SPEED"]))
            except Exception:
                demc_speed = 0.0

            # If speed is not reported but fans are running, fall back to configured IAQ range
            if demc_speed <= 0:
                try:
                    min_level = int(self.coordinator.get_modbus_data(parameter_map["REG_IAQ_SPEED_LEVEL_MIN"]))
                    max_level = int(self.coordinator.get_modbus_data(parameter_map["REG_IAQ_SPEED_LEVEL_MAX"]))
                except Exception:
                    min_level, max_level = 2, 4

                # If IAQ levels look invalid, default to Normal (Medium)
                if not (2 <= min_level <= 5 and 2 <= max_level <= 5 and min_level <= max_level):
                    return FAN_MEDIUM

                # Prefer Normal if in range, else closest of Low/High
                if min_level <= 3 <= max_level:
                    return FAN_MEDIUM
                return FAN_LOW if abs(min_level - 3) <= abs(max_level - 3) else FAN_HIGH

            # Normalize by 65535 if values look like 0..65535, else treat as percentage 0..100
            norm = demc_speed / 65535.0 if demc_speed > 100 else demc_speed / 100.0

            # Map normalized demand to Low/Medium/High (Minimum treated as Low; Maximum as High)
            if norm < 0.33:
                return FAN_LOW
            if norm < 0.66:
                return FAN_MEDIUM
            return FAN_HIGH

        # Default to preset-specific configured airflow level
        level_param_key = "REG_USERMODE_MANUAL_AIRFLOW_LEVEL_SAF"

        if preset == PRESET_MODE_CROWDED:
            level_param_key = "REG_USERMODE_CROWDED_AIRFLOW_LEVEL_SAF"
        elif preset == PRESET_MODE_REFRESH:
            level_param_key = "REG_USERMODE_REFRESH_AIRFLOW_LEVEL_SAF"
        elif preset == PRESET_MODE_FIREPLACE:
            level_param_key = "REG_USERMODE_FIREPLACE_AIRFLOW_LEVEL_SAF"
        elif preset == PRESET_MODE_AWAY:
            level_param_key = "REG_USERMODE_AWAY_AIRFLOW_LEVEL_SAF"
        # PRESET_MODE_HOLIDAY falls back to manual level setting.

        raw_level = int(self.coordinator.get_modbus_data(parameter_map[level_param_key]))

        # Map unexpected values to nearest supported fan mode
        # Allowed levels in UI: 2(Low), 3(Medium), 4(High)
        if raw_level <= 1:
            mapped = 2
        elif raw_level >= 4:
            mapped = 4
        else:
            mapped = raw_level

        return VALUE_TO_FAN_MODE_MAP.get(mapped, FAN_LOW)

    async def async_set_fan_mode(self, fan_mode: str) -> None:
        """Set new target fan mode."""
        # Handle explicit Off
        if fan_mode == FAN_OFF:
            mode = 0
        else:
            mode = FAN_MODE_TO_VALUE_MAP[fan_mode]
        try:
            await self.coordinator.set_modbus_data(parameter_map["REG_USERMODE_MANUAL_AIRFLOW_LEVEL_SAF"], mode)
        except (asyncio.exceptions.TimeoutError, ConnectionError) as exc:
            raise HomeAssistantError from exc
        finally:
            await self.coordinator.async_refresh()

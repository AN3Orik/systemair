"""The Systemair integration."""

from __future__ import annotations

import asyncio.exceptions
from dataclasses import dataclass
from typing import TYPE_CHECKING

from homeassistant.components.number import (
    NumberDeviceClass,
    NumberEntity,
    NumberEntityDescription,
    NumberMode,
)
from homeassistant.const import (
    CONCENTRATION_PARTS_PER_MILLION,
    PERCENTAGE,
    EntityCategory,
    UnitOfTemperature,
    UnitOfTime,
)
from homeassistant.exceptions import HomeAssistantError

from .entity import SystemairEntity
from .modbus import ModbusParameter, parameter_map
from .profiles import DEVICE_PROFILE_SAVE
from .profiles.entities import resolve_profile_entity_register

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import SystemairDataUpdateCoordinator
    from .data import SystemairConfigEntry
    from .profiles.base import DeviceProfile


@dataclass(kw_only=True, frozen=True)
class SystemairNumberEntityDescription(NumberEntityDescription):
    """Describes a Systemair number entity."""

    registry: ModbusParameter


NUMBERS: tuple[SystemairNumberEntityDescription, ...] = (
    SystemairNumberEntityDescription(
        key="time_delay_holiday",
        translation_key="time_delay_holiday",
        entity_category=EntityCategory.CONFIG,
        device_class=NumberDeviceClass.DURATION,
        native_step=1,
        mode=NumberMode.SLIDER,
        native_unit_of_measurement=UnitOfTime.DAYS,
        registry=parameter_map["REG_USERMODE_HOLIDAY_TIME"],
    ),
    SystemairNumberEntityDescription(
        key="time_delay_away",
        translation_key="time_delay_away",
        entity_category=EntityCategory.CONFIG,
        device_class=NumberDeviceClass.DURATION,
        native_step=1,
        mode=NumberMode.SLIDER,
        native_unit_of_measurement=UnitOfTime.HOURS,
        registry=parameter_map["REG_USERMODE_AWAY_TIME"],
    ),
    SystemairNumberEntityDescription(
        key="time_delay_fireplace",
        translation_key="time_delay_fireplace",
        entity_category=EntityCategory.CONFIG,
        device_class=NumberDeviceClass.DURATION,
        native_step=1,
        mode=NumberMode.SLIDER,
        native_unit_of_measurement=UnitOfTime.MINUTES,
        registry=parameter_map["REG_USERMODE_FIREPLACE_TIME"],
    ),
    SystemairNumberEntityDescription(
        key="time_delay_refresh",
        translation_key="time_delay_refresh",
        entity_category=EntityCategory.CONFIG,
        device_class=NumberDeviceClass.DURATION,
        native_step=1,
        mode=NumberMode.SLIDER,
        native_unit_of_measurement=UnitOfTime.MINUTES,
        registry=parameter_map["REG_USERMODE_REFRESH_TIME"],
    ),
    SystemairNumberEntityDescription(
        key="time_delay_crowded",
        translation_key="time_delay_crowded",
        entity_category=EntityCategory.CONFIG,
        device_class=NumberDeviceClass.DURATION,
        native_step=1,
        mode=NumberMode.SLIDER,
        native_unit_of_measurement=UnitOfTime.HOURS,
        registry=parameter_map["REG_USERMODE_CROWDED_TIME"],
    ),
    SystemairNumberEntityDescription(
        key="filter_period",
        translation_key="filter_period",
        entity_category=EntityCategory.CONFIG,
        icon="mdi:filter-cog",
        native_step=1,
        mode=NumberMode.SLIDER,
        native_unit_of_measurement=UnitOfTime.MONTHS,
        registry=parameter_map["REG_FILTER_PERIOD"],
    ),
    SystemairNumberEntityDescription(
        key="eco_mode_temperature_offset",
        translation_key="eco_mode_temperature_offset",
        entity_category=EntityCategory.CONFIG,
        device_class=NumberDeviceClass.TEMPERATURE,
        native_step=0.1,
        mode=NumberMode.BOX,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        registry=parameter_map["REG_ECO_T_Y1_OFFSET"],
    ),
    SystemairNumberEntityDescription(
        key="free_cooling_outdoor_low_limit",
        translation_key="free_cooling_outdoor_low_limit",
        entity_category=EntityCategory.CONFIG,
        device_class=NumberDeviceClass.TEMPERATURE,
        native_step=0.1,
        mode=NumberMode.BOX,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        registry=parameter_map["REG_FREE_COOLING_OUTDOOR_NIGHTTIME_DEACTIVATION_LOW_T_LIMIT"],
    ),
    SystemairNumberEntityDescription(
        key="free_cooling_outdoor_high_limit",
        translation_key="free_cooling_outdoor_high_limit",
        entity_category=EntityCategory.CONFIG,
        device_class=NumberDeviceClass.TEMPERATURE,
        native_step=0.1,
        mode=NumberMode.BOX,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        registry=parameter_map["REG_FREE_COOLING_OUTDOOR_NIGHTTIME_DEACTIVATION_HIGH_T_LIMIT"],
    ),
    SystemairNumberEntityDescription(
        key="free_cooling_room_cancel_temp",
        translation_key="free_cooling_room_cancel_temp",
        entity_category=EntityCategory.CONFIG,
        device_class=NumberDeviceClass.TEMPERATURE,
        native_step=0.1,
        mode=NumberMode.BOX,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        registry=parameter_map["REG_FREE_COOLING_ROOM_CANCEL_T"],
    ),
    SystemairNumberEntityDescription(
        key="free_cooling_start_time_hours",
        translation_key="free_cooling_start_time_hours",
        entity_category=EntityCategory.CONFIG,
        native_step=1,
        mode=NumberMode.BOX,
        registry=parameter_map["REG_FREE_COOLING_START_TIME_H"],
    ),
    SystemairNumberEntityDescription(
        key="free_cooling_start_time_minutes",
        translation_key="free_cooling_start_time_minutes",
        entity_category=EntityCategory.CONFIG,
        native_step=1,
        mode=NumberMode.BOX,
        registry=parameter_map["REG_FREE_COOLING_START_TIME_M"],
    ),
    SystemairNumberEntityDescription(
        key="free_cooling_end_time_hours",
        translation_key="free_cooling_end_time_hours",
        entity_category=EntityCategory.CONFIG,
        native_step=1,
        mode=NumberMode.BOX,
        registry=parameter_map["REG_FREE_COOLING_END_TIME_H"],
    ),
    SystemairNumberEntityDescription(
        key="free_cooling_end_time_minutes",
        translation_key="free_cooling_end_time_minutes",
        entity_category=EntityCategory.CONFIG,
        native_step=1,
        mode=NumberMode.BOX,
        registry=parameter_map["REG_FREE_COOLING_END_TIME_M"],
    ),
    SystemairNumberEntityDescription(
        key="heating_circ_pump_start_temp",
        translation_key="heating_circ_pump_start_temp",
        entity_category=EntityCategory.CONFIG,
        device_class=NumberDeviceClass.TEMPERATURE,
        native_step=0.1,
        mode=NumberMode.BOX,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        registry=parameter_map["REG_HEATER_CIRC_PUMP_START_T"],
    ),
    SystemairNumberEntityDescription(
        key="heating_circ_pump_stop_delay",
        translation_key="heating_circ_pump_stop_delay",
        entity_category=EntityCategory.CONFIG,
        device_class=NumberDeviceClass.DURATION,
        native_step=1,
        mode=NumberMode.BOX,
        native_unit_of_measurement=UnitOfTime.MINUTES,
        registry=parameter_map["REG_HEATER_CIRC_PUMP_STOP_DELAY"],
    ),
    SystemairNumberEntityDescription(
        key="cooling_circ_pump_stop_delay",
        translation_key="cooling_circ_pump_stop_delay",
        entity_category=EntityCategory.CONFIG,
        device_class=NumberDeviceClass.DURATION,
        native_step=1,
        mode=NumberMode.BOX,
        native_unit_of_measurement=UnitOfTime.MINUTES,
        registry=parameter_map["REG_COOLER_CIRC_PUMP_STOP_DELAY"],
    ),
    SystemairNumberEntityDescription(
        key="changeover_circ_pump_start_temp",
        translation_key="changeover_circ_pump_start_temp",
        entity_category=EntityCategory.CONFIG,
        device_class=NumberDeviceClass.TEMPERATURE,
        native_step=0.1,
        mode=NumberMode.BOX,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        registry=parameter_map["REG_CHANGE_OVER_CIRC_PUMP_START_T"],
    ),
    SystemairNumberEntityDescription(
        key="changeover_circ_pump_stop_delay",
        translation_key="changeover_circ_pump_stop_delay",
        entity_category=EntityCategory.CONFIG,
        device_class=NumberDeviceClass.DURATION,
        native_step=1,
        mode=NumberMode.BOX,
        native_unit_of_measurement=UnitOfTime.MINUTES,
        registry=parameter_map["REG_CHANGE_OVER_CIRC_PUMP_STOP_DELAY"],
    ),
    SystemairNumberEntityDescription(
        key="extra_controller_circ_pump_start_temp",
        translation_key="extra_controller_circ_pump_start_temp",
        entity_category=EntityCategory.CONFIG,
        device_class=NumberDeviceClass.TEMPERATURE,
        native_step=0.1,
        mode=NumberMode.BOX,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        registry=parameter_map["REG_EXTRA_CONTROLLER_CIRC_PUMP_START_T"],
    ),
    SystemairNumberEntityDescription(
        key="extra_controller_circ_pump_stop_delay",
        translation_key="extra_controller_circ_pump_stop_delay",
        entity_category=EntityCategory.CONFIG,
        device_class=NumberDeviceClass.DURATION,
        native_step=1,
        mode=NumberMode.BOX,
        native_unit_of_measurement=UnitOfTime.MINUTES,
        registry=parameter_map["REG_EXTRA_CONTROLLER_CIRC_PUMP_STOP_DELAY"],
    ),
    SystemairNumberEntityDescription(
        key="modbus_co2_input",
        translation_key="modbus_co2_input",
        entity_category=EntityCategory.CONFIG,
        device_class=NumberDeviceClass.CO2,
        native_step=1,
        mode=NumberMode.BOX,
        native_unit_of_measurement=CONCENTRATION_PARTS_PER_MILLION,
        icon="mdi:molecule-co2",
        registry=parameter_map["REG_SENSOR_MODBUS_CO2"],
    ),
    SystemairNumberEntityDescription(
        key="modbus_rh_input",
        translation_key="modbus_rh_input",
        entity_category=EntityCategory.CONFIG,
        device_class=NumberDeviceClass.HUMIDITY,
        native_step=1,
        mode=NumberMode.BOX,
        native_unit_of_measurement=PERCENTAGE,
        icon="mdi:water-percent",
        registry=parameter_map["REG_SENSOR_MODBUS_RHS"],
    ),
    SystemairNumberEntityDescription(
        key="rh_setpoint_summer",
        translation_key="rh_setpoint_summer",
        entity_category=EntityCategory.CONFIG,
        device_class=NumberDeviceClass.HUMIDITY,
        native_step=1,
        mode=NumberMode.SLIDER,
        native_unit_of_measurement=PERCENTAGE,
        icon="mdi:water-percent",
        registry=parameter_map["REG_DEMC_RH_SETTINGS_SP_SUMMER"],
    ),
    SystemairNumberEntityDescription(
        key="rh_setpoint_winter",
        translation_key="rh_setpoint_winter",
        entity_category=EntityCategory.CONFIG,
        device_class=NumberDeviceClass.HUMIDITY,
        native_step=1,
        mode=NumberMode.SLIDER,
        native_unit_of_measurement=PERCENTAGE,
        icon="mdi:water-percent",
        registry=parameter_map["REG_DEMC_RH_SETTINGS_SP_WINTER"],
    ),
    SystemairNumberEntityDescription(
        key="fan_level_saf_min_rpm",
        translation_key="fan_level_saf_min_rpm",
        entity_category=EntityCategory.CONFIG,
        native_step=10,
        mode=NumberMode.BOX,
        native_unit_of_measurement="RPM",
        icon="mdi:fan-speed-1",
        registry=parameter_map["REG_FAN_LEVEL_SAF_MIN_RPM"],
    ),
    SystemairNumberEntityDescription(
        key="fan_level_eaf_min_rpm",
        translation_key="fan_level_eaf_min_rpm",
        entity_category=EntityCategory.CONFIG,
        native_step=10,
        mode=NumberMode.BOX,
        native_unit_of_measurement="RPM",
        icon="mdi:fan-speed-1",
        registry=parameter_map["REG_FAN_LEVEL_EAF_MIN_RPM"],
    ),
    SystemairNumberEntityDescription(
        key="fan_level_saf_low_rpm",
        translation_key="fan_level_saf_low_rpm",
        entity_category=EntityCategory.CONFIG,
        native_step=10,
        mode=NumberMode.BOX,
        native_unit_of_measurement="RPM",
        icon="mdi:fan-speed-1",
        registry=parameter_map["REG_FAN_LEVEL_SAF_LOW_RPM"],
    ),
    SystemairNumberEntityDescription(
        key="fan_level_eaf_low_rpm",
        translation_key="fan_level_eaf_low_rpm",
        entity_category=EntityCategory.CONFIG,
        native_step=10,
        mode=NumberMode.BOX,
        native_unit_of_measurement="RPM",
        icon="mdi:fan-speed-1",
        registry=parameter_map["REG_FAN_LEVEL_EAF_LOW_RPM"],
    ),
    SystemairNumberEntityDescription(
        key="fan_level_saf_normal_rpm",
        translation_key="fan_level_saf_normal_rpm",
        entity_category=EntityCategory.CONFIG,
        native_step=10,
        mode=NumberMode.BOX,
        native_unit_of_measurement="RPM",
        icon="mdi:fan-speed-2",
        registry=parameter_map["REG_FAN_LEVEL_SAF_NORMAL_RPM"],
    ),
    SystemairNumberEntityDescription(
        key="fan_level_eaf_normal_rpm",
        translation_key="fan_level_eaf_normal_rpm",
        entity_category=EntityCategory.CONFIG,
        native_step=10,
        mode=NumberMode.BOX,
        native_unit_of_measurement="RPM",
        icon="mdi:fan-speed-2",
        registry=parameter_map["REG_FAN_LEVEL_EAF_NORMAL_RPM"],
    ),
    SystemairNumberEntityDescription(
        key="fan_level_saf_high_rpm",
        translation_key="fan_level_saf_high_rpm",
        entity_category=EntityCategory.CONFIG,
        native_step=10,
        mode=NumberMode.BOX,
        native_unit_of_measurement="RPM",
        icon="mdi:fan-speed-3",
        registry=parameter_map["REG_FAN_LEVEL_SAF_HIGH_RPM"],
    ),
    SystemairNumberEntityDescription(
        key="fan_level_eaf_high_rpm",
        translation_key="fan_level_eaf_high_rpm",
        entity_category=EntityCategory.CONFIG,
        native_step=10,
        mode=NumberMode.BOX,
        native_unit_of_measurement="RPM",
        icon="mdi:fan-speed-3",
        registry=parameter_map["REG_FAN_LEVEL_EAF_HIGH_RPM"],
    ),
    SystemairNumberEntityDescription(
        key="fan_level_saf_max_rpm",
        translation_key="fan_level_saf_max_rpm",
        entity_category=EntityCategory.CONFIG,
        native_step=10,
        mode=NumberMode.BOX,
        native_unit_of_measurement="RPM",
        icon="mdi:fan-speed-3",
        registry=parameter_map["REG_FAN_LEVEL_SAF_MAX_RPM"],
    ),
    SystemairNumberEntityDescription(
        key="fan_level_eaf_max_rpm",
        translation_key="fan_level_eaf_max_rpm",
        entity_category=EntityCategory.CONFIG,
        native_step=10,
        mode=NumberMode.BOX,
        native_unit_of_measurement="RPM",
        icon="mdi:fan-speed-3",
        registry=parameter_map["REG_FAN_LEVEL_EAF_MAX_RPM"],
    ),
)


def _profile_number_descriptions(profile: DeviceProfile) -> tuple[SystemairNumberEntityDescription, ...]:
    """Return number descriptions for the active device profile."""
    if profile.profile_id == DEVICE_PROFILE_SAVE:
        return NUMBERS

    descriptions: list[SystemairNumberEntityDescription] = []
    for desc in profile.entities.numbers:
        registry = resolve_profile_entity_register(profile, desc, "number")
        if registry is None:
            continue
        descriptions.append(
            SystemairNumberEntityDescription(
                key=desc.key,
                translation_key=desc.translation_key,
                native_unit_of_measurement=desc.native_unit_of_measurement,
                entity_category=desc.entity_category,
                mode=desc.mode or NumberMode.BOX,
                native_step=1,
                registry=registry,
            )
        )
    return tuple(descriptions)


async def async_setup_entry(
    _hass: HomeAssistant,
    entry: SystemairConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up number from a config entry."""
    async_add_entities(
        SystemairNumber(
            coordinator=entry.runtime_data.coordinator,
            entity_description=entity_description,
        )
        for entity_description in _profile_number_descriptions(entry.runtime_data.profile)
    )


class SystemairNumber(SystemairEntity, NumberEntity):
    """Representation of a Systemair Number."""

    entity_description: SystemairNumberEntityDescription

    def __init__(
        self,
        coordinator: SystemairDataUpdateCoordinator,
        entity_description: SystemairNumberEntityDescription,
    ) -> None:
        """Initialize the number class."""
        super().__init__(coordinator)

        self.entity_description = entity_description
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}-{entity_description.key}"

        # Apply scale_factor to min/max values if present
        scale_factor = entity_description.registry.scale_factor or 1
        self.native_min_value = float(entity_description.registry.min_value or 0) / scale_factor
        self.native_max_value = float(entity_description.registry.max_value or 100) / scale_factor

    @property
    def native_value(self) -> float | None:
        """Return the state of the number."""
        return self.coordinator.get_modbus_data(self.entity_description.registry)

    async def async_set_native_value(self, value: float) -> None:
        """Update the current value."""
        try:
            await self.coordinator.set_modbus_data(self.entity_description.registry, value)
        except (asyncio.exceptions.TimeoutError, ConnectionError) as exc:
            raise HomeAssistantError from exc
        finally:
            await self.coordinator.async_refresh()

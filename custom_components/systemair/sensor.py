"""Sensor platform for Systemair0."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.components.sensor.const import SensorDeviceClass, SensorStateClass
from homeassistant.const import PERCENTAGE, REVOLUTIONS_PER_MINUTE, EntityCategory, UnitOfTemperature, UnitOfTime

from .entity import SystemairEntity
from .modbus import ModbusParameter, alarm_parameters, parameter_map

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import SystemairDataUpdateCoordinator
    from .data import SystemairConfigEntry

ALARM_STATE_TO_VALUE_MAP = {
    "Inactive": 0,
    "Active": 1,
    "Waiting": 2,
    "Cleared Error Active": 3,
}

VALUE_MAP_TO_ALARM_STATE = {value: key for key, value in ALARM_STATE_TO_VALUE_MAP.items()}

IAQ_LEVEL_MAP = {0: "Perfect", 1: "Good", 2: "Improving"}
DEMAND_CONTROLLER_MAP = {0: "CO2", 1: "RH"}
DEFROSTING_STATE_MAP = {
    0: "Normal",
    1: "Bypass",
    2: "Stop",
    3: "Secondary air",
    4: "Error",
}


@dataclass(kw_only=True, frozen=True)
class SystemairSensorEntityDescription(SensorEntityDescription):
    """Describes a Systemair sensor entity."""

    registry: ModbusParameter


ENTITY_DESCRIPTIONS = (
    SystemairSensorEntityDescription(
        key="outside_air_temperature",
        translation_key="outside_air_temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        registry=parameter_map["REG_SENSOR_OAT"],
    ),
    SystemairSensorEntityDescription(
        key="extract_air_temperature",
        translation_key="extract_air_temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        registry=parameter_map["REG_SENSOR_PDM_EAT_VALUE"],
    ),
    SystemairSensorEntityDescription(
        key="supply_air_temperature",
        translation_key="supply_air_temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        registry=parameter_map["REG_SENSOR_SAT"],
    ),
    SystemairSensorEntityDescription(
        key="overheat_temperature",
        translation_key="overheat_temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        registry=parameter_map["REG_SENSOR_OHT"],
    ),
    SystemairSensorEntityDescription(
        key="extract_air_relative_humidity",
        translation_key="extract_air_relative_humidity",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=PERCENTAGE,
        registry=parameter_map["REG_SENSOR_RHS_PDM"],
    ),
    SystemairSensorEntityDescription(
        key="meter_saf_rpm",
        translation_key="meter_saf_rpm",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=REVOLUTIONS_PER_MINUTE,
        registry=parameter_map["REG_SENSOR_RPM_SAF"],
    ),
    SystemairSensorEntityDescription(
        key="meter_saf_reg_speed",
        translation_key="meter_saf_reg_speed",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=PERCENTAGE,
        registry=parameter_map["REG_OUTPUT_SAF"],
    ),
    SystemairSensorEntityDescription(
        key="meter_eaf_rpm",
        translation_key="meter_eaf_rpm",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=REVOLUTIONS_PER_MINUTE,
        registry=parameter_map["REG_SENSOR_RPM_EAF"],
    ),
    SystemairSensorEntityDescription(
        key="meter_eaf_reg_speed",
        translation_key="meter_eaf_reg_speed",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=PERCENTAGE,
        registry=parameter_map["REG_OUTPUT_EAF"],
    ),
    SystemairSensorEntityDescription(
        key="heater_output_value",
        translation_key="heater_output_value",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=PERCENTAGE,
        registry=parameter_map["REG_PWM_TRIAC_OUTPUT"],
    ),
    SystemairSensorEntityDescription(
        key="filter_remaining_time",
        translation_key="filter_remaining_time",
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTime.SECONDS,
        registry=parameter_map["REG_FILTER_REMAINING_TIME_L"],
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SystemairSensorEntityDescription(
        key="iaq_level",
        translation_key="iaq_level",
        icon="mdi:air-filter",
        device_class=SensorDeviceClass.ENUM,
        options=["Perfect", "Good", "Improving"],
        registry=parameter_map["REG_IAQ_LEVEL"],
    ),
    SystemairSensorEntityDescription(
        key="demand_active_controller",
        translation_key="demand_active_controller",
        icon="mdi:tune-variant",
        device_class=SensorDeviceClass.ENUM,
        options=["CO2", "RH"],
        registry=parameter_map["REG_DEMC_ACTIVE_CONTROLLER"],
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SystemairSensorEntityDescription(
        key="defrosting_state",
        translation_key="defrosting_state",
        icon="mdi:snowflake-alert",
        device_class=SensorDeviceClass.ENUM,
        options=["Normal", "Bypass", "Stop", "Secondary air", "Error"],
        registry=parameter_map["REG_DEFROSTING_STATE"],
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    *(
        SystemairSensorEntityDescription(
            key=f"alarm_{param.short.lower()}",
            name=param.description,
            device_class=SensorDeviceClass.ENUM,
            options=["Inactive", "Active", "Waiting", "Cleared Error Active"],
            registry=param,
            entity_category=EntityCategory.DIAGNOSTIC,
        )
        for param in alarm_parameters.values()
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001 Unused function argument: `hass`
    entry: SystemairConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    async_add_entities(
        SystemairSensor(
            coordinator=entry.runtime_data.coordinator,
            entity_description=entity_description,
        )
        for entity_description in ENTITY_DESCRIPTIONS
    )


class SystemairSensor(SystemairEntity, SensorEntity):
    """Systemair Sensor class."""

    _attr_has_entity_name = True

    entity_description: SystemairSensorEntityDescription

    def __init__(
        self,
        coordinator: SystemairDataUpdateCoordinator,
        entity_description: SystemairSensorEntityDescription,
    ) -> None:
        """Initialize the sensor class."""
        super().__init__(coordinator)
        self.entity_description = entity_description
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}-{entity_description.key}"

    @property
    def native_value(self) -> str | None:
        """Return the native value of the sensor."""
        value = self.coordinator.get_modbus_data(self.entity_description.registry)
        value = int(value)

        key = self.entity_description.key
        if key == "iaq_level":
            return IAQ_LEVEL_MAP.get(value)
        if key == "demand_active_controller":
            return DEMAND_CONTROLLER_MAP.get(value)
        if key == "defrosting_state":
            return DEFROSTING_STATE_MAP.get(value)

        if self.device_class == SensorDeviceClass.ENUM:
            return VALUE_MAP_TO_ALARM_STATE.get(value, "Inactive")

        return str(value)
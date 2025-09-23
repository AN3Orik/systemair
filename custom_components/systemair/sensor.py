"""Sensor platform for Systemair."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import (
    PERCENTAGE,
    REVOLUTIONS_PER_MINUTE,
    EntityCategory,
    UnitOfPower,
    UnitOfTemperature,
    UnitOfTime,
)

from .const import MODEL_SPECS
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


@dataclass(kw_only=True, frozen=True)
class SystemairPowerSensorEntityDescription(SensorEntityDescription):
    """Describes a Systemair power sensor entity."""


POWER_SENSORS: tuple[SystemairPowerSensorEntityDescription, ...] = (
    SystemairPowerSensorEntityDescription(
        key="supply_fan_power",
        translation_key="supply_fan_power",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SystemairPowerSensorEntityDescription(
        key="extract_fan_power",
        translation_key="extract_fan_power",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SystemairPowerSensorEntityDescription(
        key="total_power",
        translation_key="total_power",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        state_class=SensorStateClass.MEASUREMENT,
    ),
)

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
            translation_key=f"alarm_{param.short.lower()}",
            device_class=SensorDeviceClass.ENUM,
            options=["Inactive", "Active", "Waiting", "Cleared Error Active"],
            registry=param,
            entity_category=EntityCategory.DIAGNOSTIC,
        )
        for param in alarm_parameters.values()
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001
    entry: SystemairConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    coordinator = entry.runtime_data.coordinator

    sensors = [SystemairSensor(coordinator=coordinator, entity_description=desc) for desc in ENTITY_DESCRIPTIONS]
    power_sensors = [SystemairPowerSensor(coordinator=coordinator, entity_description=desc) for desc in POWER_SENSORS]

    async_add_entities(sensors + power_sensors)


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


class SystemairPowerSensor(SystemairEntity, SensorEntity):
    """Systemair Power Sensor class for calculated values."""

    _attr_has_entity_name = True
    entity_description: SystemairPowerSensorEntityDescription

    def __init__(
        self,
        coordinator: SystemairDataUpdateCoordinator,
        entity_description: SystemairPowerSensorEntityDescription,
    ) -> None:
        """Initialize the power sensor class."""
        super().__init__(coordinator)
        self.entity_description = entity_description
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}-{entity_description.key}"

    @property
    def native_value(self) -> float | None:
        """Return the calculated power consumption."""
        model = self.coordinator.config_entry.runtime_data.model
        specs = MODEL_SPECS.get(model)
        if not specs:
            return None

        # Get fan counts from specs, defaulting to 0 if not present
        num_supply_fans = specs.get("supply_fans", 0)
        num_extract_fans = specs.get("extract_fans", 0)
        total_fans = num_supply_fans + num_extract_fans

        # Calculate power per fan
        power_per_fan = 0
        if total_fans > 0:
            power_per_fan = specs.get("fan_power", 0) / total_fans

        # Get current fan speeds and heater status
        supply_fan_pct = self.coordinator.get_modbus_data(parameter_map["REG_OUTPUT_SAF"])
        extract_fan_pct = self.coordinator.get_modbus_data(parameter_map["REG_OUTPUT_EAF"])
        heater_on = self.coordinator.get_modbus_data(parameter_map["REG_OUTPUT_TRIAC"])

        if supply_fan_pct is None or extract_fan_pct is None or heater_on is None:
            return None

        # Calculate power for each component
        supply_power = (supply_fan_pct / 100) * power_per_fan * num_supply_fans
        extract_power = (extract_fan_pct / 100) * power_per_fan * num_extract_fans
        heater_power = specs.get("heater_power", 0) if heater_on else 0

        # Return the correct value based on the sensor's key
        key = self.entity_description.key
        if key == "supply_fan_power":
            return round(supply_power, 1)
        if key == "extract_fan_power":
            return round(extract_power, 1)
        if key == "total_power":
            return round(supply_power + extract_power + heater_power, 1)

        return None

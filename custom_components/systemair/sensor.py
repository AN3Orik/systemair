"""Sensor platform for Systemair."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, ClassVar

from homeassistant.components.sensor import (
    RestoreSensor,
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import (
    PERCENTAGE,
    REVOLUTIONS_PER_MINUTE,
    EntityCategory,
    UnitOfEnergy,
    UnitOfPower,
    UnitOfTemperature,
    UnitOfTime,
)
from homeassistant.util import dt as dt_util

from .const import MODEL_SPECS
from .entity import SystemairEntity
from .modbus import (
    ModbusParameter,
    alarm_log_registers,
    alarm_parameters,
    parameter_map,
)

if TYPE_CHECKING:
    from datetime import datetime, timedelta

    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import SystemairDataUpdateCoordinator
    from .data import SystemairConfigEntry


YEAR_2000_THRESHOLD = 100

ALARM_ID_TO_NAME_MAP = {
    0: "Frost protection",
    1: "Frost protection temperature sensor",
    2: "Defrosting error",
    3: "Supply air fan feedback",
    4: "Extract air fan feedback",
    5: "Supply air fan control error",
    6: "Extract air fan control error",
    7: "Emergency thermostat",
    8: "Plate heat exchanger bypass damper",
    9: "Rotary heat exchanger rotation guard",
    10: "Secondary air damper",
    11: "Outdoor air temperature sensor",
    12: "Overheat temperature sensor",
    13: "Supply air temperature sensor",
    14: "Room air temperature sensor",
    15: "Extract air temperature sensor",
    16: "Extra controller temperature sensor",
    17: "Efficiency temperature sensor",
    18: "Inbuilt relative humidity sensor",
    19: "Inbuilt extract air temperature sensor",
    20: "Filter",
    21: "Extra controller alarm",
    22: "External stop",
    23: "Manual fan stop",
    24: "Heater overheat",
    25: "Low supply air temperature",
    26: "External CO2 sensor",
    27: "External relative humidity sensor",
    28: "Manual output mode",
    29: "Fire alarm",
    30: "Filter warning",
    34: "Bypass damper feedback",
}

ALARM_LOG_STATE_MAP = {
    0: "Inactive",
    1: "Active",
    2: "Counter increasing",
    3: "Acknowledged",
}

ALARM_STATE_TO_VALUE_MAP = {
    "Inactive": 0,
    "Active": 1,
    "Waiting": 2,
    "Cleared Error Active": 3,
}
VALUE_MAP_TO_ALARM_STATE = {value: key for key, value in ALARM_STATE_TO_VALUE_MAP.items()}
IAQ_LEVEL_MAP = {0: "Perfect", 1: "Good", 2: "Improving"}
DEMAND_CONTROLLER_MAP = {0: "CO2", 1: "RH"}
AUTO_MODE_SOURCE_MAP = {
    0: "External control",
    1: "Demand control",
    2: "Week schedule",
    3: "Configuration fault",
}
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

    registry: ModbusParameter | None = None


@dataclass(kw_only=True, frozen=True)
class SystemairPowerSensorEntityDescription(SensorEntityDescription):
    """Describes a Systemair power sensor entity."""


@dataclass(kw_only=True, frozen=True)
class SystemairEnergySensorEntityDescription(SensorEntityDescription):
    """Describes a Systemair energy sensor entity."""

    power_sensor_key: str


ENERGY_SENSORS: tuple[SystemairEnergySensorEntityDescription, ...] = (
    SystemairEnergySensorEntityDescription(
        key="supply_fan_energy",
        translation_key="supply_fan_energy",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        power_sensor_key="supply_fan_power",
    ),
    SystemairEnergySensorEntityDescription(
        key="extract_fan_energy",
        translation_key="extract_fan_energy",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        power_sensor_key="extract_fan_power",
    ),
    SystemairEnergySensorEntityDescription(
        key="total_energy",
        translation_key="total_energy",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        power_sensor_key="total_power",
    ),
)

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
        key="heating_demand",
        translation_key="heating_demand",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=PERCENTAGE,
        registry=parameter_map["REG_HEATER_FROM_SATC"],
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SystemairSensorEntityDescription(
        key="heater_analog_output",
        translation_key="heater_analog_output",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=PERCENTAGE,
        registry=parameter_map["REG_OUTPUT_Y1_ANALOG"],
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SystemairSensorEntityDescription(
        key="changeover_analog_output",
        translation_key="changeover_analog_output",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=PERCENTAGE,
        registry=parameter_map["REG_OUTPUT_Y1_Y3_ANALOG"],
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SystemairSensorEntityDescription(
        key="heating_circ_pump_counter",
        translation_key="heating_circ_pump_counter",
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTime.SECONDS,
        registry=parameter_map["REG_HEATER_CIRC_PUMP_COUNTER"],
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SystemairSensorEntityDescription(
        key="cooling_circ_pump_counter",
        translation_key="cooling_circ_pump_counter",
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTime.SECONDS,
        registry=parameter_map["REG_COOLER_CIRC_PUMP_COUNTER"],
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SystemairSensorEntityDescription(
        key="changeover_circ_pump_counter",
        translation_key="changeover_circ_pump_counter",
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTime.SECONDS,
        registry=parameter_map["REG_CHANGE_OVER_CIRC_PUMP_COUNTER"],
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SystemairSensorEntityDescription(
        key="extra_controller_circ_pump_counter",
        translation_key="extra_controller_circ_pump_counter",
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTime.SECONDS,
        registry=parameter_map["REG_EXTRA_CONTROLLER_CIRC_PUMP_COUNTER"],
        entity_category=EntityCategory.DIAGNOSTIC,
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
        key="auto_mode_source",
        translation_key="auto_mode_source",
        icon="mdi:auto-mode",
        device_class=SensorDeviceClass.ENUM,
        options=["External control", "Demand control", "Week schedule", "Configuration fault"],
        registry=parameter_map["REG_DEMC_AUTO_MODE_SOURCE"],
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
    SystemairSensorEntityDescription(
        key="alarm_history",
        translation_key="alarm_history",
        icon="mdi:history",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
)


async def async_setup_entry(
    _hass: HomeAssistant,
    entry: SystemairConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    coordinator = entry.runtime_data.coordinator

    power_sensors_map = {desc.key: SystemairPowerSensor(coordinator=coordinator, entity_description=desc) for desc in POWER_SENSORS}

    sensors = [SystemairSensor(coordinator=coordinator, entity_description=desc) for desc in ENTITY_DESCRIPTIONS]
    power_sensors = list(power_sensors_map.values())

    energy_sensors = [
        SystemairEnergySensor(
            coordinator=coordinator,
            entity_description=desc,
            power_sensor=power_sensors_map[desc.power_sensor_key],
        )
        for desc in ENERGY_SENSORS
    ]

    async_add_entities(sensors + power_sensors + energy_sensors)


class SystemairSensor(SystemairEntity, SensorEntity):
    """Systemair Sensor class for all sensors."""

    entity_description: SystemairSensorEntityDescription

    _KEY_TO_MAP: ClassVar[dict[str, dict[int, str]]] = {
        "iaq_level": IAQ_LEVEL_MAP,
        "demand_active_controller": DEMAND_CONTROLLER_MAP,
        "auto_mode_source": AUTO_MODE_SOURCE_MAP,
        "defrosting_state": DEFROSTING_STATE_MAP,
    }

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
        if self.coordinator.data is None:
            return None

        key = self.entity_description.key

        if key == "alarm_history":
            first_log = alarm_log_registers[0]
            alarm_id_reg = first_log["id"]
            alarm_id = self.coordinator.data.get(str(alarm_id_reg - 1))
            if alarm_id is None or alarm_id == 0:
                return "No recent alarms"
            return ALARM_ID_TO_NAME_MAP.get(int(alarm_id), f"Unknown ID: {alarm_id}")

        value = self.coordinator.get_modbus_data(self.entity_description.registry)
        if value is None:
            return None

        int_value = int(value)
        result = None

        if value_map := self._KEY_TO_MAP.get(key):
            result = value_map.get(int_value)
        elif self.device_class == SensorDeviceClass.ENUM:
            result = VALUE_MAP_TO_ALARM_STATE.get(int_value, "Inactive")
        else:
            result = str(value)

        return result

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return the state attributes."""
        if self.entity_description.key != "alarm_history":
            return None

        if self.coordinator.data is None:
            return {"history": []}

        history = []
        data = self.coordinator.data

        for log_regs in alarm_log_registers:
            alarm_id = data.get(str(log_regs["id"] - 1))
            if alarm_id is None or alarm_id == 0:
                continue

            state_val = data.get(str(log_regs["state"] - 1))
            year = data.get(str(log_regs["year"] - 1))
            month = data.get(str(log_regs["month"] - 1))
            day = data.get(str(log_regs["day"] - 1))
            hour = data.get(str(log_regs["hour"] - 1))
            minute = data.get(str(log_regs["minute"] - 1))
            second = data.get(str(log_regs["second"] - 1))

            timestamp = "Unknown time"
            if all(v is not None for v in [year, month, day, hour, minute, second]):
                year_val = year + 2000 if year < YEAR_2000_THRESHOLD else year
                timestamp = f"{year_val:04d}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}:{second:02d}"

            history.append(
                {
                    "alarm": ALARM_ID_TO_NAME_MAP.get(alarm_id, f"Unknown ID: {alarm_id}"),
                    "status": ALARM_LOG_STATE_MAP.get(state_val, "Unknown"),
                    "timestamp": timestamp,
                }
            )

        return {"history": history}


class SystemairPowerSensor(SystemairEntity, SensorEntity):
    """Systemair Power Sensor class for calculated values."""

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
        if self.coordinator.data is None:
            return None

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
        supply_power = (float(supply_fan_pct) / 100) * power_per_fan * num_supply_fans
        extract_power = (float(extract_fan_pct) / 100) * power_per_fan * num_extract_fans
        heater_power = specs.get("heater_power", 0) if heater_on else 0

        power_map = {
            "supply_fan_power": round(supply_power, 1),
            "extract_fan_power": round(extract_power, 1),
            "total_power": round(supply_power + extract_power + heater_power, 1),
        }

        return power_map.get(self.entity_description.key)


class SystemairEnergySensor(SystemairEntity, RestoreSensor):
    """Systemair Energy Sensor class."""

    entity_description: SystemairEnergySensorEntityDescription

    def __init__(
        self,
        coordinator: SystemairDataUpdateCoordinator,
        entity_description: SystemairEnergySensorEntityDescription,
        power_sensor: SystemairPowerSensor,
    ) -> None:
        """Initialize the energy sensor."""
        super().__init__(coordinator)
        self.entity_description = entity_description
        self._power_sensor = power_sensor
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}-{entity_description.key}"
        self._last_update: datetime | None = None

    async def async_added_to_hass(self) -> None:
        """Handle entity which provides long-term statistics."""
        await super().async_added_to_hass()

        last_sensor_data = await self.async_get_last_sensor_data()
        if last_sensor_data:
            self._attr_native_value = last_sensor_data.native_value

        if (
            (last_state := await self.async_get_last_state())
            and "last_update" in last_state.attributes
            and last_state.attributes["last_update"] is not None
        ):
            self._last_update = dt_util.parse_datetime(last_state.attributes["last_update"])

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes."""
        return {"last_update": self._last_update.isoformat() if self._last_update else None}

    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        now = dt_util.utcnow()
        power_w = self._power_sensor.native_value

        if power_w is None or self._last_update is None:
            self._last_update = now
            self.async_write_ha_state()
            return

        time_delta: timedelta = now - self._last_update
        energy_increment_kwh = (power_w / 1000) * (time_delta.total_seconds() / 3600)

        current_value = self.native_value or 0
        self._attr_native_value = round(current_value + energy_increment_kwh, 4)

        self._last_update = now
        self.async_write_ha_state()

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
    CONCENTRATION_PARTS_PER_MILLION,
    PERCENTAGE,
    REVOLUTIONS_PER_MINUTE,
    EntityCategory,
    UnitOfEnergy,
    UnitOfPower,
    UnitOfTemperature,
    UnitOfTime,
    UnitOfVolumeFlowRate,
)
from homeassistant.util import dt as dt_util

from .const import (
    CONF_ENABLE_ALARM_HISTORY,
    CONF_EXTRACT_AIRFLOW_MAX,
    CONF_SUPPLY_AIRFLOW_MAX,
    DEFAULT_BASE_POWER,
    DEFAULT_ENABLE_ALARM_HISTORY,
    DEFAULT_FAN_POWER_EXPONENT,
    DEFAULT_FAN_POWER_FACTOR,
    resolve_model_specs,
)
from .entity import SystemairEntity, homesolution_supported_descriptions, remove_unsupported_homesolution_entities
from .modbus import (
    ModbusParameter,
    alarm_log_registers,
    alarm_parameters,
    parameter_map,
)
from .profiles import DEVICE_PROFILE_SAVE
from .profiles.entities import resolve_profile_entity_register
from .systemair_api.utils.constants import UserModes

if TYPE_CHECKING:
    from datetime import datetime, timedelta

    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import SystemairDataUpdateCoordinator
    from .data import SystemairConfigEntry
    from .profiles.base import DeviceProfile


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
AUTO_MODE_CONFIGURATION_FAULT = 3
AUTO_MODE_NOT_CONFIGURED = 4
AUTO_MODE_SOURCE_MAP = {
    0: "External control",
    1: "Demand control",
    2: "Week schedule",
    AUTO_MODE_CONFIGURATION_FAULT: "Configuration fault",
    AUTO_MODE_NOT_CONFIGURED: "Auto mode not configured",
}
DEFROSTING_STATE_MAP = {
    0: "Normal",
    1: "Bypass",
    2: "Stop",
    3: "Secondary air",
    4: "Error",
}
SUMMER_WINTER_STATE_MAP = {0: "Summer", 1: "Winter", 2: "Spring/Autumn"}


def calculate_airflow(max_airflow_m3h: float | None, fan_output_percentage: float | None) -> int | None:
    """Estimate whole-unit airflow from the live fan output percentage."""
    if max_airflow_m3h is None or fan_output_percentage is None:
        return None

    output_percentage = min(max(float(fan_output_percentage), 0), 100)
    return round(float(max_airflow_m3h) * output_percentage / 100)


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


@dataclass(kw_only=True, frozen=True)
class SystemairAirflowSensorEntityDescription(SensorEntityDescription):
    """Describes a calculated whole-unit airflow sensor."""

    fan_side: str


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

AIRFLOW_SENSORS: tuple[SystemairAirflowSensorEntityDescription, ...] = (
    SystemairAirflowSensorEntityDescription(
        key="supply_airflow",
        translation_key="supply_airflow",
        device_class=SensorDeviceClass.VOLUME_FLOW_RATE,
        native_unit_of_measurement=UnitOfVolumeFlowRate.CUBIC_METERS_PER_HOUR,
        state_class=SensorStateClass.MEASUREMENT,
        fan_side="supply",
    ),
    SystemairAirflowSensorEntityDescription(
        key="extract_airflow",
        translation_key="extract_airflow",
        device_class=SensorDeviceClass.VOLUME_FLOW_RATE,
        native_unit_of_measurement=UnitOfVolumeFlowRate.CUBIC_METERS_PER_HOUR,
        state_class=SensorStateClass.MEASUREMENT,
        fan_side="extract",
    ),
)

ENTITY_DESCRIPTIONS = (
    SystemairSensorEntityDescription(
        key="analog_input_ui_1",
        translation_key="analog_input_ui_1",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement="mV",
        registry=parameter_map["REG_INPUT_ANALOG_UI_1"],
    ),
    SystemairSensorEntityDescription(
        key="analog_input_ui_2",
        translation_key="analog_input_ui_2",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement="mV",
        registry=parameter_map["REG_INPUT_ANALOG_UI_2"],
    ),
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
        key="co2_level",
        translation_key="co2_level",
        device_class=SensorDeviceClass.CO2,
        native_unit_of_measurement=CONCENTRATION_PARTS_PER_MILLION,
        state_class=SensorStateClass.MEASUREMENT,
        registry=parameter_map["REG_DEMC_CO2_HIGHEST"],
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
        key="heat_exchanger_output",
        translation_key="heat_exchanger_output",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=PERCENTAGE,
        registry=parameter_map["REG_OUTPUT_Y2_ANALOG"],
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
        options=list(AUTO_MODE_SOURCE_MAP.values()),
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
    SystemairSensorEntityDescription(
        key="summer_winter_state",
        translation_key="summer_winter_state",
        icon="mdi:sun-snowflake",
        device_class=SensorDeviceClass.ENUM,
        options=["Summer", "Winter", "Spring/Autumn"],
        registry=parameter_map["REG_SUMMER_WINTER_STATE"],
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


def _profile_sensor_descriptions(profile: DeviceProfile) -> tuple[SystemairSensorEntityDescription, ...]:
    """Return sensor descriptions for the active device profile."""
    if profile.profile_id == DEVICE_PROFILE_SAVE:
        return ENTITY_DESCRIPTIONS

    descriptions: list[SystemairSensorEntityDescription] = []
    for desc in profile.entities.sensors:
        registry = resolve_profile_entity_register(profile, desc, "sensor")
        if registry is None:
            continue
        descriptions.append(
            SystemairSensorEntityDescription(
                key=desc.key,
                translation_key=desc.translation_key,
                device_class=desc.device_class,
                state_class=desc.state_class,
                native_unit_of_measurement=desc.native_unit_of_measurement,
                entity_category=desc.entity_category,
                icon=desc.icon,
                registry=registry,
            )
        )
    return tuple(descriptions)


def airflow_sensor_descriptions(model: str, profile: DeviceProfile) -> tuple[SystemairAirflowSensorEntityDescription, ...]:
    """Return airflow sensors supported by the selected unit model."""
    specs = resolve_model_specs(model, profile.model_aliases)
    if specs is None or specs.get("max_airflow_m3h") is None or profile.power_registers is None:
        return ()

    return tuple(desc for desc in AIRFLOW_SENSORS if specs.get(f"{desc.fan_side}_fans", 0))


async def async_setup_entry(
    hass: HomeAssistant,
    entry: SystemairConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    coordinator = entry.runtime_data.coordinator
    profile = entry.runtime_data.profile

    descriptions = _profile_sensor_descriptions(profile)
    supported_descriptions = homesolution_supported_descriptions(coordinator, descriptions)
    remove_unsupported_homesolution_entities(hass, coordinator, "sensor", descriptions, supported_descriptions)
    sensors = [SystemairSensor(coordinator=coordinator, entity_description=desc) for desc in supported_descriptions]
    entities: list[SensorEntity] = [*sensors]

    if profile.power_registers is not None:
        airflow_sensors = [
            SystemairAirflowSensor(coordinator=coordinator, entity_description=desc)
            for desc in airflow_sensor_descriptions(entry.runtime_data.model, profile)
        ]
        power_sensors_map = {desc.key: SystemairPowerSensor(coordinator=coordinator, entity_description=desc) for desc in POWER_SENSORS}
        power_sensors = list(power_sensors_map.values())
        energy_sensors = [
            SystemairEnergySensor(
                coordinator=coordinator,
                entity_description=desc,
                power_sensor=power_sensors_map[desc.power_sensor_key],
            )
            for desc in ENERGY_SENSORS
        ]
        entities.extend([*airflow_sensors, *power_sensors, *energy_sensors])

    async_add_entities(entities)


class SystemairSensor(SystemairEntity, SensorEntity):
    """Systemair Sensor class for all sensors."""

    entity_description: SystemairSensorEntityDescription

    _KEY_TO_MAP: ClassVar[dict[str, dict[int, str]]] = {
        "iaq_level": IAQ_LEVEL_MAP,
        "demand_active_controller": DEMAND_CONTROLLER_MAP,
        "auto_mode_source": AUTO_MODE_SOURCE_MAP,
        "defrosting_state": DEFROSTING_STATE_MAP,
        "summer_winter_state": SUMMER_WINTER_STATE_MAP,
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
    def available(self) -> bool:
        """Return if entity is available."""
        if self.entity_description.key == "alarm_history":
            enabled = self.coordinator.config_entry.options.get(CONF_ENABLE_ALARM_HISTORY, DEFAULT_ENABLE_ALARM_HISTORY)
            has_history = not self._is_homesolution or self.coordinator.has_raw_register(alarm_log_registers[0]["id"])
            return enabled and has_history and super().available
        return super().available

    @property
    def native_value(self) -> str | None:
        """Return the native value of the sensor."""
        if self.coordinator.data is None:
            return None

        key = self.entity_description.key
        if key == "alarm_history":
            return self._get_alarm_history_state()

        value = self.coordinator.get_modbus_data(self.entity_description.registry)
        if value is None:
            return None

        int_value = int(value)

        if key == "auto_mode_source" and int_value == AUTO_MODE_CONFIGURATION_FAULT:
            profile = self.coordinator.config_entry.runtime_data.profile
            user_mode_register = profile.registry.get("REG_USERMODE_MODE")
            active_user_mode = self.coordinator.get_modbus_data(user_mode_register) if user_mode_register is not None else None
            if active_user_mode is not None and int(active_user_mode) != UserModes.AUTO:
                int_value = AUTO_MODE_NOT_CONFIGURED

        if value_map := self._KEY_TO_MAP.get(key):
            return value_map.get(int_value)
        if self.device_class == SensorDeviceClass.ENUM:
            return VALUE_MAP_TO_ALARM_STATE.get(int_value, "Inactive")

        return str(value)

    def _get_alarm_history_state(self) -> str | None:
        """Get the state for the alarm history sensor."""
        if not self.coordinator.config_entry.options.get(CONF_ENABLE_ALARM_HISTORY, DEFAULT_ENABLE_ALARM_HISTORY):
            return None

        first_log = alarm_log_registers[0]
        alarm_id = self._alarm_log_value(first_log["id"])
        if alarm_id is None or alarm_id == 0:
            return "No recent alarms"
        return ALARM_ID_TO_NAME_MAP.get(int(alarm_id), f"Unknown ID: {alarm_id}")

    def _alarm_log_value(self, address_1based: int) -> int | None:
        """Read and normalize one raw alarm-log field."""
        value = self.coordinator.get_raw_register(address_1based)
        if value is None:
            return None
        try:
            return int(value)
        except (TypeError, ValueError):
            return None

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return the state attributes."""
        if self.entity_description.key != "alarm_history":
            return None

        if self.coordinator.data is None:
            return {"history": []}

        history = []

        for log_regs in alarm_log_registers:
            alarm_id = self._alarm_log_value(log_regs["id"])
            if alarm_id is None or alarm_id == 0:
                continue

            state_val = self._alarm_log_value(log_regs["state"])
            year = self._alarm_log_value(log_regs["year"])
            month = self._alarm_log_value(log_regs["month"])
            day = self._alarm_log_value(log_regs["day"])
            hour = self._alarm_log_value(log_regs["hour"])
            minute = self._alarm_log_value(log_regs["minute"])
            second = self._alarm_log_value(log_regs["second"])

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


class SystemairAirflowSensor(SystemairEntity, SensorEntity):
    """Calculated whole-unit airflow sensor."""

    entity_description: SystemairAirflowSensorEntityDescription

    def __init__(
        self,
        coordinator: SystemairDataUpdateCoordinator,
        entity_description: SystemairAirflowSensorEntityDescription,
    ) -> None:
        """Initialize the airflow sensor."""
        super().__init__(coordinator)
        self.entity_description = entity_description
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}-{entity_description.key}"

    def _airflow_context(self) -> tuple[float, float, str] | None:
        """Return fan output, reference maximum, and reference source."""
        profile = self.coordinator.config_entry.runtime_data.profile
        specs = resolve_model_specs(self.coordinator.config_entry.runtime_data.model, profile.model_aliases)
        power_registers = profile.power_registers
        if specs is None or power_registers is None:
            return None

        is_supply = self.entity_description.fan_side == "supply"
        register_key = power_registers.supply_output if is_supply else power_registers.extract_output
        register = profile.registry.get(register_key)
        if register is None:
            return None

        fan_output = self.coordinator.get_modbus_data(register)
        if fan_output is None:
            return None

        option_key = CONF_SUPPLY_AIRFLOW_MAX if is_supply else CONF_EXTRACT_AIRFLOW_MAX
        calibrated_max = self.coordinator.config_entry.options.get(option_key)
        passport_max = specs.get("max_airflow_m3h")
        reference_max = calibrated_max if calibrated_max is not None else passport_max
        if reference_max is None:
            return None

        output_percentage = min(max(float(fan_output), 0), 100)
        reference_source = "calibrated" if calibrated_max is not None else "passport"
        return output_percentage, float(reference_max), reference_source

    @property
    def available(self) -> bool:
        """Return whether live output and a reference maximum are available."""
        return super().available and self._airflow_context() is not None

    @property
    def native_value(self) -> int | None:
        """Return the calculated whole-unit airflow."""
        if self.coordinator.data is None or (context := self._airflow_context()) is None:
            return None

        output_percentage, reference_max, _reference_source = context
        return calculate_airflow(reference_max, output_percentage)

    @property
    def extra_state_attributes(self) -> dict[str, float | str]:
        """Expose the live percentage and maximum used by the estimate."""
        if (context := self._airflow_context()) is None:
            return {}

        output_percentage, reference_max, reference_source = context
        return {
            "fan_output_percentage": output_percentage,
            "reference_max_airflow_m3h": reference_max,
            "reference_source": reference_source,
        }


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
    def available(self) -> bool:
        """Return whether all inputs needed for the calculation are available."""
        return super().available and self.native_value is not None

    @property
    def native_value(self) -> float | None:
        """Return the calculated power consumption."""
        if self.coordinator.data is None:
            return None

        profile = self.coordinator.config_entry.runtime_data.profile
        power_registers = profile.power_registers
        if power_registers is None:
            return None

        model = self.coordinator.config_entry.runtime_data.model
        specs = resolve_model_specs(model, profile.model_aliases)
        if not specs:
            return None

        # fan_power is the documented maximum power for one fan. Fan load is non-linear by output percentage.
        num_supply_fans = specs.get("supply_fans", 0)
        num_extract_fans = specs.get("extract_fans", 0)
        base_power = specs.get("base_power", DEFAULT_BASE_POWER)
        fan_power = specs.get("fan_power", 0) * specs.get("fan_power_factor", DEFAULT_FAN_POWER_FACTOR)
        fan_power_exponent = specs.get("fan_power_exponent", DEFAULT_FAN_POWER_EXPONENT)

        supply_register = profile.registry.get(power_registers.supply_output)
        extract_register = profile.registry.get(power_registers.extract_output)
        heater_register = profile.registry.get(power_registers.heater_output) if power_registers.heater_output else None
        if supply_register is None or extract_register is None:
            return None

        supply_fan_pct = self.coordinator.get_modbus_data(supply_register)
        extract_fan_pct = self.coordinator.get_modbus_data(extract_register)
        heater_output = self.coordinator.get_modbus_data(heater_register) if heater_register else 0

        if (num_supply_fans and supply_fan_pct is None) or (num_extract_fans and extract_fan_pct is None):
            return None

        if supply_fan_pct is None:
            supply_fan_pct = 0
        if extract_fan_pct is None:
            extract_fan_pct = 0
        if heater_output is None:
            heater_output = 0

        supply_power = ((float(supply_fan_pct) / 100) ** fan_power_exponent) * fan_power * num_supply_fans
        extract_power = ((float(extract_fan_pct) / 100) ** fan_power_exponent) * fan_power * num_extract_fans
        heater_power = specs.get("heater_power", 0)
        if power_registers.heater_output_is_percentage:
            heater_power *= float(heater_output) / 100
        elif not heater_output:
            heater_power = 0

        power_map = {
            "supply_fan_power": round(supply_power, 1),
            "extract_fan_power": round(extract_power, 1),
            "total_power": round(base_power + supply_power + extract_power + heater_power, 1),
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

    @property
    def available(self) -> bool:
        """Return whether the live power source is available."""
        return super().available and self._power_sensor.available

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

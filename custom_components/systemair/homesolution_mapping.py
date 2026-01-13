"""Mapping layer for Systemair HomeSolution."""

from typing import Any

from .const import (
    PRESET_MODE_AUTO,
    PRESET_MODE_AWAY,
    PRESET_MODE_COOKER_HOOD,
    PRESET_MODE_CROWDED,
    PRESET_MODE_FIREPLACE,
    PRESET_MODE_HOLIDAY,
    PRESET_MODE_MANUAL,
    PRESET_MODE_REFRESH,
    PRESET_MODE_VACUUM_CLEANER,
)
from .systemair_api.models.ventilation_unit import VentilationUnit
from .systemair_api.utils.constants import UserModes
from .systemair_api.utils.register_constants import RegisterConstants

# Map user modes to preset mode strings
USER_MODE_TO_PRESET = {
    UserModes.AUTO: PRESET_MODE_AUTO,
    UserModes.MANUAL: PRESET_MODE_MANUAL,
    UserModes.CROWDED: PRESET_MODE_CROWDED,
    UserModes.REFRESH: PRESET_MODE_REFRESH,
    UserModes.FIREPLACE: PRESET_MODE_FIREPLACE,
    UserModes.AWAY: PRESET_MODE_AWAY,
    UserModes.HOLIDAY: PRESET_MODE_HOLIDAY,
    UserModes.COOKER_HOOD: PRESET_MODE_COOKER_HOOD,
    UserModes.VACUUM_CLEANER: PRESET_MODE_VACUUM_CLEANER,
}

# Reverse map for writing
PRESET_TO_USER_MODE = {v: k for k, v in USER_MODE_TO_PRESET.items()}

# Map preset mode strings to Modbus values (1-based index from climate.py)
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
    # CDI modes not typically exposed in HomeSolution API directly as modes but handled if needed
}


def _get_preset_mode_value(unit: VentilationUnit) -> int:
    """Get the preset mode value (1-based index) from the unit's user mode."""
    preset = USER_MODE_TO_PRESET.get(unit.user_mode)
    return PRESET_MODE_TO_VALUE_MAP.get(preset, 2)  # Default to MANUAL (2) if unknown


def _get_fan_mode_value(unit: VentilationUnit) -> int:
    """Get fan mode value.

    In climate.py:
    FAN_OFF: 0
    FAN_LOW: 2
    FAN_MEDIUM: 3
    FAN_HIGH: 4
    """  # noqa: D213
    if unit.airflow is None:
        return 3  # Medium/Normal default

    # Unit airflow is 1-5 (1=Off, 2=Low, 3=Normal, 4=High, 5=Max)
    # We map to the values expected by climate.py entity
    if unit.airflow == 1:
        return 0  # Off
    if unit.airflow == 2:  # noqa: PLR2004
        return 2  # Low
    if unit.airflow == 3:  # noqa: PLR2004
        return 3  # Medium
    if unit.airflow >= 4:  # noqa: PLR2004
        return 4  # High
    return 3


def _get_active_alarms_count(unit: VentilationUnit) -> int:
    """Count active alarms."""
    if unit.active_alarms:
        return 1
    # Check individual alarm types if available
    if unit.alarm_type_a or unit.alarm_type_b or unit.alarm_type_c:
        return 1
    return 0


def _is_alarm_active(unit: VentilationUnit, _alarm_id: int) -> int:
    """Check if a specific alarm is active."""
    # This function is not currently used by the mapping logic directly,
    # as alarms are mapped to specific registers.
    # But for completeness, we can check if the unit has active alarms.
    return 1 if unit.active_alarms else 0


def get_reg(unit: VentilationUnit, register_id: int, default: Any = None) -> Any:
    """Get register value safely."""
    return unit.registers.get(register_id, default)


# Mapping from Modbus register short names to lambda functions extracting data from VentilationUnit
HOMESOLUTION_MAPPING = {
    # Temperature sensors
    "REG_SENSOR_OAT": lambda unit: unit.registers.get(RegisterConstants.REG_MAINBOARD_SENSOR_OAT, unit.temperatures.get("oat", 0) * 10)
    / 10.0
    if unit.registers.get(RegisterConstants.REG_MAINBOARD_SENSOR_OAT) is not None or unit.temperatures.get("oat") is not None
    else None,
    "REG_SENSOR_SAT": lambda unit: unit.registers.get(RegisterConstants.REG_MAINBOARD_SENSOR_SAT, unit.temperatures.get("sat", 0) * 10)
    / 10.0
    if unit.registers.get(RegisterConstants.REG_MAINBOARD_SENSOR_SAT) is not None or unit.temperatures.get("sat") is not None
    else None,
    "REG_SENSOR_RAT": lambda unit: unit.registers.get(RegisterConstants.REG_MAINBOARD_SENSOR_RAT, unit.temperatures.get("room", 0) * 10)
    / 10.0
    if unit.registers.get(RegisterConstants.REG_MAINBOARD_SENSOR_RAT) is not None or unit.temperatures.get("room") is not None
    else None,
    "REG_SENSOR_EAT": lambda unit: unit.registers.get(RegisterConstants.REG_MAINBOARD_SENSOR_EAT, unit.temperatures.get("eat", 0) * 10)
    / 10.0
    if unit.registers.get(RegisterConstants.REG_MAINBOARD_SENSOR_EAT) is not None or unit.temperatures.get("eat") is not None
    else None,
    "REG_TC_SP": lambda unit: unit.registers.get(RegisterConstants.REG_MAINBOARD_TC_SP, unit.temperatures.get("setpoint", 0) * 10) / 10.0
    if unit.registers.get(RegisterConstants.REG_MAINBOARD_TC_SP) is not None or unit.temperatures.get("setpoint") is not None
    else None,
    # Humidity
    "REG_SENSOR_RHS_PDM": lambda unit: unit.registers.get(RegisterConstants.REG_MAINBOARD_SENSOR_RHS_PDM, unit.humidity),
    # Operation Mode & Fan
    "REG_USERMODE_MODE": lambda unit: unit.registers.get(RegisterConstants.REG_MAINBOARD_USERMODE_MODE_HMI, unit.user_mode),
    "REG_USERMODE_HMI_CHANGE_REQUEST": _get_preset_mode_value,
    "REG_OUTPUT_SAF": lambda unit: unit.registers.get(RegisterConstants.REG_MAINBOARD_SPEED_INDICATION_APP, unit.airflow) * 20
    if unit.registers.get(RegisterConstants.REG_MAINBOARD_SPEED_INDICATION_APP, unit.airflow)
    else 0,
    "REG_OUTPUT_EAF": lambda unit: unit.registers.get(RegisterConstants.REG_MAINBOARD_SPEED_INDICATION_APP, unit.airflow) * 20
    if unit.registers.get(RegisterConstants.REG_MAINBOARD_SPEED_INDICATION_APP, unit.airflow)
    else 0,
    "REG_USERMODE_MANUAL_AIRFLOW_LEVEL_SAF": _get_fan_mode_value,
    "REG_FAN_MANUAL_STOP_ALLOWED": lambda unit: unit.registers.get(RegisterConstants.REG_MAINBOARD_FAN_MANUAL_STOP_ALLOWED),
    "REG_SENSOR_RPM_SAF": lambda unit: unit.registers.get(RegisterConstants.REG_MAINBOARD_SENSOR_RPM_SAF),
    "REG_SENSOR_RPM_EAF": lambda unit: unit.registers.get(RegisterConstants.REG_MAINBOARD_SENSOR_RPM_EAF),
    # Binary Sensors / Status
    "REG_FUNCTION_ACTIVE_HEATER": lambda unit: unit.registers.get(RegisterConstants.REG_MAINBOARD_FUNCTION_ACTIVE_HEATING),
    "REG_FUNCTION_ACTIVE_COOLER": lambda unit: unit.registers.get(RegisterConstants.REG_MAINBOARD_FUNCTION_ACTIVE_COOLING),
    "REG_OUTPUT_TRIAC": lambda unit: 1 if unit.registers.get(RegisterConstants.REG_MAINBOARD_FUNCTION_ACTIVE_HEATING) else 0,
    "REG_OUTPUT_Y3_DIGITAL": lambda unit: 1 if unit.registers.get(RegisterConstants.REG_MAINBOARD_FUNCTION_ACTIVE_COOLING) else 0,
    "REG_FUNCTION_ACTIVE_HEAT_RECOVERY": lambda unit: unit.registers.get(RegisterConstants.REG_MAINBOARD_FUNCTION_ACTIVE_HEAT_RECOVERY),
    "REG_FUNCTION_ACTIVE_FREE_COOLING": lambda unit: unit.registers.get(RegisterConstants.REG_MAINBOARD_FUNCTION_ACTIVE_FREE_COOLING),
    "REG_FUNCTION_ACTIVE_DEFROSTING": lambda unit: unit.registers.get(RegisterConstants.REG_MAINBOARD_FUNCTION_ACTIVE_DEFROSTING),
    "REG_FUNCTION_ACTIVE_COOLING_RECOVERY": lambda unit: unit.registers.get(
        RegisterConstants.REG_MAINBOARD_FUNCTION_ACTIVE_COOLING_RECOVERY
    ),
    "REG_FUNCTION_ACTIVE_MOISTURE_TRANSFER": lambda unit: unit.registers.get(
        RegisterConstants.REG_MAINBOARD_FUNCTION_ACTIVE_MOISTURE_TRANSFER
    ),
    "REG_FUNCTION_ACTIVE_SECONDARY_AIR": lambda unit: unit.registers.get(RegisterConstants.REG_MAINBOARD_FUNCTION_ACTIVE_SECONDARY_AIR),
    "REG_FUNCTION_ACTIVE_VACUUM_CLEANER": lambda unit: unit.registers.get(RegisterConstants.REG_MAINBOARD_FUNCTION_ACTIVE_VACUUM_CLEANER),
    "REG_FUNCTION_ACTIVE_COOKER_HOOD": lambda unit: unit.registers.get(RegisterConstants.REG_MAINBOARD_FUNCTION_ACTIVE_COOKER_HOOD),
    "REG_FUNCTION_ACTIVE_HEATER_COOL_DOWN": lambda unit: unit.registers.get(
        RegisterConstants.REG_MAINBOARD_FUNCTION_ACTIVE_HEATER_COOL_DOWN
    ),
    "REG_FUNCTION_ACTIVE_PRESSURE_GUARD": lambda unit: unit.registers.get(RegisterConstants.REG_MAINBOARD_FUNCTION_ACTIVE_PRESSURE_GUARD),
    "REG_ECO_MODE_ON_OFF": lambda unit: unit.registers.get(RegisterConstants.REG_MAINBOARD_ECO_MODE_ON_OFF),
    "REG_ECO_FUNCTION_ACTIVE": lambda unit: unit.registers.get(RegisterConstants.REG_MAINBOARD_FUNCTION_ACTIVE_ECO_MODE),
    "REG_PASSIVE_HOUSE_ACTIVATION": lambda unit: unit.registers.get(RegisterConstants.REG_MAINBOARD_PASSIVE_HOUSE_ACTIVATION),
    # Filter
    "REG_FILTER_REMAINING_TIME_L": lambda unit: unit.registers.get(RegisterConstants.REG_MAINBOARD_FILTER_REMAINING_TIME_L, 0) * 24 * 3600,
    "REG_FILTER_PERIOD": lambda unit: unit.registers.get(RegisterConstants.REG_MAINBOARD_FILTER_PERIOD, 6),
    # Demand Control
    "REG_MAINBOARD_DEMC_RH_SETTINGS_ON_OFF": lambda unit: unit.registers.get(RegisterConstants.REG_MAINBOARD_DEMC_RH_SETTINGS_ON_OFF),
    "REG_MAINBOARD_DEMC_CO2_SETTINGS_ON_OFF": lambda unit: unit.registers.get(RegisterConstants.REG_MAINBOARD_DEMC_CO2_SETTINGS_ON_OFF),
    # User Mode Times
    "REG_USERMODE_HOLIDAY_TIME": lambda unit: unit.registers.get(RegisterConstants.REG_MAINBOARD_USERMODE_HOLIDAY_TIME),
    "REG_USERMODE_AWAY_TIME": lambda unit: unit.registers.get(RegisterConstants.REG_MAINBOARD_USERMODE_AWAY_TIME),
    "REG_USERMODE_FIREPLACE_TIME": lambda unit: unit.registers.get(RegisterConstants.REG_MAINBOARD_USERMODE_FIREPLACE_TIME),
    "REG_USERMODE_REFRESH_TIME": lambda unit: unit.registers.get(RegisterConstants.REG_MAINBOARD_USERMODE_REFRESH_TIME),
    "REG_USERMODE_CROWDED_TIME": lambda unit: unit.registers.get(RegisterConstants.REG_MAINBOARD_USERMODE_CROWDED_TIME),
    "REG_USERMODE_REMAINING_TIME_L": lambda unit: unit.registers.get(RegisterConstants.REG_MAINBOARD_USERMODE_REMAINING_TIME_L),
    # Alarms
    "REG_ALARM_HARDWARE_ERROR": lambda unit: 1 if _get_active_alarms_count(unit) > 0 else 0,
    "REG_ALARM_SAF_CTRL_ALARM": lambda unit: get_reg(unit, RegisterConstants.REG_ALARM_SAF_CTRL_ALARM),
    "REG_ALARM_SAF_CTRL_CLEAR_ALARM": lambda unit: get_reg(unit, RegisterConstants.REG_ALARM_SAF_CTRL_CLEAR_ALARM),
    "REG_ALARM_SAF_CTRL_TIMESTAMP_L": lambda unit: get_reg(unit, RegisterConstants.REG_ALARM_SAF_CTRL_TIMESTAMP_L),
    "REG_ALARM_EAF_CTRL_ALARM": lambda unit: get_reg(unit, RegisterConstants.REG_ALARM_EAF_CTRL_ALARM),
    "REG_ALARM_EAF_CTRL_CLEAR_ALARM": lambda unit: get_reg(unit, RegisterConstants.REG_ALARM_EAF_CTRL_CLEAR_ALARM),
    "REG_ALARM_EAF_CTRL_TIMESTAMP_L": lambda unit: get_reg(unit, RegisterConstants.REG_ALARM_EAF_CTRL_TIMESTAMP_L),
    "REG_ALARM_FROST_PROT_ALARM": lambda unit: get_reg(unit, RegisterConstants.REG_ALARM_FROST_PROT_ALARM),
    "REG_ALARM_FROST_PROT_CLEAR_ALARM": lambda unit: get_reg(unit, RegisterConstants.REG_ALARM_FROST_PROT_CLEAR_ALARM),
    "REG_ALARM_FROST_PROT_TIMESTAMP_L": lambda unit: get_reg(unit, RegisterConstants.REG_ALARM_FROST_PROT_TIMESTAMP_L),
    "REG_ALARM_DEFROSTING_ALARM": lambda unit: get_reg(unit, RegisterConstants.REG_ALARM_DEFROSTING_ALARM),
    "REG_ALARM_DEFROSTING_CLEAR_ALARM": lambda unit: get_reg(unit, RegisterConstants.REG_ALARM_DEFROSTING_CLEAR_ALARM),
    "REG_ALARM_DEFROSTING_TIMESTAMP_L": lambda unit: get_reg(unit, RegisterConstants.REG_ALARM_DEFROSTING_TIMESTAMP_L),
    "REG_ALARM_SAF_RPM_ALARM": lambda unit: get_reg(unit, RegisterConstants.REG_ALARM_SAF_RPM_ALARM),
    "REG_ALARM_SAF_RPM_CLEAR_ALARM": lambda unit: get_reg(unit, RegisterConstants.REG_ALARM_SAF_RPM_CLEAR_ALARM),
    "REG_ALARM_SAF_RPM_TIMESTAMP_L": lambda unit: get_reg(unit, RegisterConstants.REG_ALARM_SAF_RPM_TIMESTAMP_L),
    "REG_ALARM_EAF_RPM_ALARM": lambda unit: get_reg(unit, RegisterConstants.REG_ALARM_EAF_RPM_ALARM),
    "REG_ALARM_EAF_RPM_CLEAR_ALARM": lambda unit: get_reg(unit, RegisterConstants.REG_ALARM_EAF_RPM_CLEAR_ALARM),
    "REG_ALARM_EAF_RPM_TIMESTAMP_L": lambda unit: get_reg(unit, RegisterConstants.REG_ALARM_EAF_RPM_TIMESTAMP_L),
    "REG_ALARM_FPT_ALARM": lambda unit: get_reg(unit, RegisterConstants.REG_ALARM_FPT_ALARM),
    "REG_ALARM_FPT_CLEAR_ALARM": lambda unit: get_reg(unit, RegisterConstants.REG_ALARM_FPT_CLEAR_ALARM),
    "REG_ALARM_FPT_TIMESTAMP_L": lambda unit: get_reg(unit, RegisterConstants.REG_ALARM_FPT_TIMESTAMP_L),
    "REG_ALARM_OAT_ALARM": lambda unit: get_reg(unit, RegisterConstants.REG_ALARM_OAT_ALARM),
    "REG_ALARM_OAT_CLEAR_ALARM": lambda unit: get_reg(unit, RegisterConstants.REG_ALARM_OAT_CLEAR_ALARM),
    "REG_ALARM_OAT_TIMESTAMP_L": lambda unit: get_reg(unit, RegisterConstants.REG_ALARM_OAT_TIMESTAMP_L),
    "REG_ALARM_SAT_ALARM": lambda unit: get_reg(unit, RegisterConstants.REG_ALARM_SAT_ALARM),
    "REG_ALARM_SAT_CLEAR_ALARM": lambda unit: get_reg(unit, RegisterConstants.REG_ALARM_SAT_CLEAR_ALARM),
    "REG_ALARM_SAT_TIMESTAMP_L": lambda unit: get_reg(unit, RegisterConstants.REG_ALARM_SAT_TIMESTAMP_L),
    "REG_ALARM_RAT_ALARM": lambda unit: get_reg(unit, RegisterConstants.REG_ALARM_RAT_ALARM),
    "REG_ALARM_RAT_CLEAR_ALARM": lambda unit: get_reg(unit, RegisterConstants.REG_ALARM_RAT_CLEAR_ALARM),
    "REG_ALARM_RAT_TIMESTAMP_L": lambda unit: get_reg(unit, RegisterConstants.REG_ALARM_RAT_TIMESTAMP_L),
    "REG_ALARM_EAT_ALARM": lambda unit: get_reg(unit, RegisterConstants.REG_ALARM_EAT_ALARM),
    "REG_ALARM_EAT_CLEAR_ALARM": lambda unit: get_reg(unit, RegisterConstants.REG_ALARM_EAT_CLEAR_ALARM),
    "REG_ALARM_EAT_TIMESTAMP_L": lambda unit: get_reg(unit, RegisterConstants.REG_ALARM_EAT_TIMESTAMP_L),
    "REG_ALARM_ECT_ALARM": lambda unit: get_reg(unit, RegisterConstants.REG_ALARM_ECT_ALARM),
    "REG_ALARM_ECT_CLEAR_ALARM": lambda unit: get_reg(unit, RegisterConstants.REG_ALARM_ECT_CLEAR_ALARM),
    "REG_ALARM_ECT_TIMESTAMP_L": lambda unit: get_reg(unit, RegisterConstants.REG_ALARM_ECT_TIMESTAMP_L),
    "REG_ALARM_EFT_ALARM": lambda unit: get_reg(unit, RegisterConstants.REG_ALARM_EFT_ALARM),
    "REG_ALARM_EFT_CLEAR_ALARM": lambda unit: get_reg(unit, RegisterConstants.REG_ALARM_EFT_CLEAR_ALARM),
    "REG_ALARM_EFT_TIMESTAMP_L": lambda unit: get_reg(unit, RegisterConstants.REG_ALARM_EFT_TIMESTAMP_L),
    "REG_ALARM_OHT_ALARM": lambda unit: get_reg(unit, RegisterConstants.REG_ALARM_OHT_ALARM),
    "REG_ALARM_OHT_CLEAR_ALARM": lambda unit: get_reg(unit, RegisterConstants.REG_ALARM_OHT_CLEAR_ALARM),
    "REG_ALARM_OHT_TIMESTAMP_L": lambda unit: get_reg(unit, RegisterConstants.REG_ALARM_OHT_TIMESTAMP_L),
    "REG_ALARM_EMT_ALARM": lambda unit: get_reg(unit, RegisterConstants.REG_ALARM_EMT_ALARM),
    "REG_ALARM_EMT_CLEAR_ALARM": lambda unit: get_reg(unit, RegisterConstants.REG_ALARM_EMT_CLEAR_ALARM),
    "REG_ALARM_EMT_TIMESTAMP_L": lambda unit: get_reg(unit, RegisterConstants.REG_ALARM_EMT_TIMESTAMP_L),
    "REG_ALARM_RGS_ALARM": lambda unit: get_reg(unit, RegisterConstants.REG_ALARM_RGS_ALARM),
    "REG_ALARM_RGS_CLEAR_ALARM": lambda unit: get_reg(unit, RegisterConstants.REG_ALARM_RGS_CLEAR_ALARM),
    "REG_ALARM_RGS_TIMESTAMP_L": lambda unit: get_reg(unit, RegisterConstants.REG_ALARM_RGS_TIMESTAMP_L),
    "REG_ALARM_BYS_ALARM": lambda unit: get_reg(unit, RegisterConstants.REG_ALARM_BYS_ALARM),
    "REG_ALARM_BYS_CLEAR_ALARM": lambda unit: get_reg(unit, RegisterConstants.REG_ALARM_BYS_CLEAR_ALARM),
    "REG_ALARM_BYS_TIMESTAMP_L": lambda unit: get_reg(unit, RegisterConstants.REG_ALARM_BYS_TIMESTAMP_L),
    "REG_ALARM_SECONDARY_AIR_ALARM": lambda unit: get_reg(unit, RegisterConstants.REG_ALARM_SECONDARY_AIR_ALARM),
    "REG_ALARM_SECONDARY_AIR_CLEAR_ALARM": lambda unit: get_reg(unit, RegisterConstants.REG_ALARM_SECONDARY_AIR_CLEAR_ALARM),
    "REG_ALARM_SECONDARY_AIR_TIMESTAMP_L": lambda unit: get_reg(unit, RegisterConstants.REG_ALARM_SECONDARY_AIR_TIMESTAMP_L),
    "REG_ALARM_FILTER_ALARM": lambda unit: get_reg(unit, RegisterConstants.REG_ALARM_FILTER_ALARM),
    "REG_ALARM_FILTER_CLEAR_ALARM": lambda unit: get_reg(unit, RegisterConstants.REG_ALARM_FILTER_CLEAR_ALARM),
    "REG_ALARM_FILTER_TIMESTAMP_L": lambda unit: get_reg(unit, RegisterConstants.REG_ALARM_FILTER_TIMESTAMP_L),
    "REG_ALARM_EXTRA_CONTROLLER_ALARM": lambda unit: get_reg(unit, RegisterConstants.REG_ALARM_EXTRA_CONTROLLER_ALARM),
    "REG_ALARM_EXTRA_CONTROLLER_CLEAR_ALARM": lambda unit: get_reg(unit, RegisterConstants.REG_ALARM_EXTRA_CONTROLLER_CLEAR_ALARM),
    "REG_ALARM_EXTRA_CONTROLLER_TIMESTAMP_L": lambda unit: get_reg(unit, RegisterConstants.REG_ALARM_EXTRA_CONTROLLER_TIMESTAMP_L),
    "REG_ALARM_EXTERNAL_STOP_ALARM": lambda unit: get_reg(unit, RegisterConstants.REG_ALARM_EXTERNAL_STOP_ALARM),
    "REG_ALARM_EXTERNAL_STOP_CLEAR_ALARM": lambda unit: get_reg(unit, RegisterConstants.REG_ALARM_EXTERNAL_STOP_CLEAR_ALARM),
    "REG_ALARM_EXTERNAL_STOP_TIMESTAMP_L": lambda unit: get_reg(unit, RegisterConstants.REG_ALARM_EXTERNAL_STOP_TIMESTAMP_L),
    "REG_ALARM_RH_ALARM": lambda unit: get_reg(unit, RegisterConstants.REG_ALARM_RH_ALARM),
    "REG_ALARM_RH_CLEAR_ALARM": lambda unit: get_reg(unit, RegisterConstants.REG_ALARM_RH_CLEAR_ALARM),
    "REG_ALARM_RH_TIMESTAMP_L": lambda unit: get_reg(unit, RegisterConstants.REG_ALARM_RH_TIMESTAMP_L),
    "REG_ALARM_CO2_ALARM": lambda unit: get_reg(unit, RegisterConstants.REG_ALARM_CO2_ALARM),
    "REG_ALARM_CO2_CLEAR_ALARM": lambda unit: get_reg(unit, RegisterConstants.REG_ALARM_CO2_CLEAR_ALARM),
    "REG_ALARM_CO2_TIMESTAMP_L": lambda unit: get_reg(unit, RegisterConstants.REG_ALARM_CO2_TIMESTAMP_L),
    "REG_ALARM_LOW_SAT_ALARM": lambda unit: get_reg(unit, RegisterConstants.REG_ALARM_LOW_SAT_ALARM),
    "REG_ALARM_LOW_SAT_CLEAR_ALARM": lambda unit: get_reg(unit, RegisterConstants.REG_ALARM_LOW_SAT_CLEAR_ALARM),
    "REG_ALARM_LOW_SAT_TIMESTAMP_L": lambda unit: get_reg(unit, RegisterConstants.REG_ALARM_LOW_SAT_TIMESTAMP_L),
    "REG_ALARM_BYF_ALARM": lambda unit: get_reg(unit, RegisterConstants.REG_ALARM_BYF_ALARM),
    "REG_ALARM_BYF_CLEAR_ALARM": lambda unit: get_reg(unit, RegisterConstants.REG_ALARM_BYF_CLEAR_ALARM),
    "REG_ALARM_BYF_TIMESTAMP_L": lambda unit: get_reg(unit, RegisterConstants.REG_ALARM_BYF_TIMESTAMP_L),
    "REG_ALARM_PDM_RHS_ALARM": lambda unit: get_reg(unit, RegisterConstants.REG_ALARM_PDM_RHS_ALARM),
    "REG_ALARM_PDM_RHS_CLEAR_ALARM": lambda unit: get_reg(unit, RegisterConstants.REG_ALARM_PDM_RHS_CLEAR_ALARM),
    "REG_ALARM_PDM_RHS_TIMESTAMP_L": lambda unit: get_reg(unit, RegisterConstants.REG_ALARM_PDM_RHS_TIMESTAMP_L),
    "REG_ALARM_PDM_EAT_ALARM": lambda unit: get_reg(unit, RegisterConstants.REG_ALARM_PDM_EAT_ALARM),
    "REG_ALARM_PDM_EAT_CLEAR_ALARM": lambda unit: get_reg(unit, RegisterConstants.REG_ALARM_PDM_EAT_CLEAR_ALARM),
    "REG_ALARM_PDM_EAT_TIMESTAMP_L": lambda unit: get_reg(unit, RegisterConstants.REG_ALARM_PDM_EAT_TIMESTAMP_L),
    "REG_ALARM_MANUAL_FAN_STOP_ALARM": lambda unit: get_reg(unit, RegisterConstants.REG_ALARM_MANUAL_FAN_STOP_ALARM),
    "REG_ALARM_MANUAL_FAN_STOP_CLEAR_ALARM": lambda unit: get_reg(unit, RegisterConstants.REG_ALARM_MANUAL_FAN_STOP_CLEAR_ALARM),
    "REG_ALARM_MANUAL_FAN_STOP_TIMESTAMP_L": lambda unit: get_reg(unit, RegisterConstants.REG_ALARM_MANUAL_FAN_STOP_TIMESTAMP_L),
    "REG_ALARM_OVERHEAT_TEMPERATURE_ALARM": lambda unit: get_reg(unit, RegisterConstants.REG_ALARM_OVERHEAT_TEMPERATURE_ALARM),
    "REG_ALARM_OVERHEAT_TEMPERATURE_CLEAR_ALARM": lambda unit: get_reg(unit, RegisterConstants.REG_ALARM_OVERHEAT_TEMPERATURE_CLEAR_ALARM),
    "REG_ALARM_OVERHEAT_TEMPERATURE_TIMESTAMP_L": lambda unit: get_reg(unit, RegisterConstants.REG_ALARM_OVERHEAT_TEMPERATURE_TIMESTAMP_L),
    "REG_ALARM_FIRE_ALARM_ALARM": lambda unit: get_reg(unit, RegisterConstants.REG_ALARM_FIRE_ALARM_ALARM),
    "REG_ALARM_FIRE_ALARM_CLEAR_ALARM": lambda unit: get_reg(unit, RegisterConstants.REG_ALARM_FIRE_ALARM_CLEAR_ALARM),
    "REG_ALARM_FIRE_ALARM_TIMESTAMP_L": lambda unit: get_reg(unit, RegisterConstants.REG_ALARM_FIRE_ALARM_TIMESTAMP_L),
    "REG_ALARM_FILTER_WARNING_ALARM": lambda unit: get_reg(unit, RegisterConstants.REG_ALARM_FILTER_WARNING_ALARM),
    "REG_ALARM_FILTER_WARNING_CLEAR_ALARM": lambda unit: get_reg(unit, RegisterConstants.REG_ALARM_FILTER_WARNING_CLEAR_ALARM),
    "REG_ALARM_FILTER_WARNING_TIMESTAMP_L": lambda unit: get_reg(unit, RegisterConstants.REG_ALARM_FILTER_WARNING_TIMESTAMP_L),
    "REG_ALARM_MANUAL_OVERRIDE_OUTPUTS_ALARM": lambda unit: get_reg(unit, RegisterConstants.REG_ALARM_MANUAL_OVERRIDE_OUTPUTS_ALARM),
    "REG_ALARM_MANUAL_OVERRIDE_OUTPUTS_CLEAR_ALARM": lambda unit: get_reg(
        unit, RegisterConstants.REG_ALARM_MANUAL_OVERRIDE_OUTPUTS_CLEAR_ALARM
    ),
    "REG_ALARM_MANUAL_OVERRIDE_OUTPUTS_TIMESTAMP_L": lambda unit: get_reg(
        unit, RegisterConstants.REG_ALARM_MANUAL_OVERRIDE_OUTPUTS_TIMESTAMP_L
    ),
    # Schedules
    "REG_WS_DAY1_PRD1_START_H": lambda unit: get_reg(unit, RegisterConstants.REG_WS_DAY1_PRD1_START_H),
    "REG_WS_DAY1_PRD1_START_M": lambda unit: get_reg(unit, RegisterConstants.REG_WS_DAY1_PRD1_START_M),
    "REG_WS_DAY1_PRD1_END_H": lambda unit: get_reg(unit, RegisterConstants.REG_WS_DAY1_PRD1_END_H),
    "REG_WS_DAY1_PRD1_END_M": lambda unit: get_reg(unit, RegisterConstants.REG_WS_DAY1_PRD1_END_M),
    "REG_WS_DAY1_PRD1_ENABLED": lambda unit: get_reg(unit, RegisterConstants.REG_WS_DAY1_PRD1_ENABLED),
    "REG_WS_DAY1_PRD2_START_H": lambda unit: get_reg(unit, RegisterConstants.REG_WS_DAY1_PRD2_START_H),
    "REG_WS_DAY1_PRD2_START_M": lambda unit: get_reg(unit, RegisterConstants.REG_WS_DAY1_PRD2_START_M),
    "REG_WS_DAY1_PRD2_END_H": lambda unit: get_reg(unit, RegisterConstants.REG_WS_DAY1_PRD2_END_H),
    "REG_WS_DAY1_PRD2_END_M": lambda unit: get_reg(unit, RegisterConstants.REG_WS_DAY1_PRD2_END_M),
    "REG_WS_DAY1_PRD2_ENABLED": lambda unit: get_reg(unit, RegisterConstants.REG_WS_DAY1_PRD2_ENABLED),
    "REG_WS_DAY2_PRD1_START_H": lambda unit: get_reg(unit, RegisterConstants.REG_WS_DAY2_PRD1_START_H),
    "REG_WS_DAY2_PRD1_START_M": lambda unit: get_reg(unit, RegisterConstants.REG_WS_DAY2_PRD1_START_M),
    "REG_WS_DAY2_PRD1_END_H": lambda unit: get_reg(unit, RegisterConstants.REG_WS_DAY2_PRD1_END_H),
    "REG_WS_DAY2_PRD1_END_M": lambda unit: get_reg(unit, RegisterConstants.REG_WS_DAY2_PRD1_END_M),
    "REG_WS_DAY2_PRD1_ENABLED": lambda unit: get_reg(unit, RegisterConstants.REG_WS_DAY2_PRD1_ENABLED),
    "REG_WS_DAY2_PRD2_START_H": lambda unit: get_reg(unit, RegisterConstants.REG_WS_DAY2_PRD2_START_H),
    "REG_WS_DAY2_PRD2_START_M": lambda unit: get_reg(unit, RegisterConstants.REG_WS_DAY2_PRD2_START_M),
    "REG_WS_DAY2_PRD2_END_H": lambda unit: get_reg(unit, RegisterConstants.REG_WS_DAY2_PRD2_END_H),
    "REG_WS_DAY2_PRD2_END_M": lambda unit: get_reg(unit, RegisterConstants.REG_WS_DAY2_PRD2_END_M),
    "REG_WS_DAY2_PRD2_ENABLED": lambda unit: get_reg(unit, RegisterConstants.REG_WS_DAY2_PRD2_ENABLED),
    "REG_WS_DAY3_PRD1_START_H": lambda unit: get_reg(unit, RegisterConstants.REG_WS_DAY3_PRD1_START_H),
    "REG_WS_DAY3_PRD1_START_M": lambda unit: get_reg(unit, RegisterConstants.REG_WS_DAY3_PRD1_START_M),
    "REG_WS_DAY3_PRD1_END_H": lambda unit: get_reg(unit, RegisterConstants.REG_WS_DAY3_PRD1_END_H),
    "REG_WS_DAY3_PRD1_END_M": lambda unit: get_reg(unit, RegisterConstants.REG_WS_DAY3_PRD1_END_M),
    "REG_WS_DAY3_PRD1_ENABLED": lambda unit: get_reg(unit, RegisterConstants.REG_WS_DAY3_PRD1_ENABLED),
    "REG_WS_DAY3_PRD2_START_H": lambda unit: get_reg(unit, RegisterConstants.REG_WS_DAY3_PRD2_START_H),
    "REG_WS_DAY3_PRD2_START_M": lambda unit: get_reg(unit, RegisterConstants.REG_WS_DAY3_PRD2_START_M),
    "REG_WS_DAY3_PRD2_END_H": lambda unit: get_reg(unit, RegisterConstants.REG_WS_DAY3_PRD2_END_H),
    "REG_WS_DAY3_PRD2_END_M": lambda unit: get_reg(unit, RegisterConstants.REG_WS_DAY3_PRD2_END_M),
    "REG_WS_DAY3_PRD2_ENABLED": lambda unit: get_reg(unit, RegisterConstants.REG_WS_DAY3_PRD2_ENABLED),
    "REG_WS_DAY4_PRD1_START_H": lambda unit: get_reg(unit, RegisterConstants.REG_WS_DAY4_PRD1_START_H),
    "REG_WS_DAY4_PRD1_START_M": lambda unit: get_reg(unit, RegisterConstants.REG_WS_DAY4_PRD1_START_M),
    "REG_WS_DAY4_PRD1_END_H": lambda unit: get_reg(unit, RegisterConstants.REG_WS_DAY4_PRD1_END_H),
    "REG_WS_DAY4_PRD1_END_M": lambda unit: get_reg(unit, RegisterConstants.REG_WS_DAY4_PRD1_END_M),
    "REG_WS_DAY4_PRD1_ENABLED": lambda unit: get_reg(unit, RegisterConstants.REG_WS_DAY4_PRD1_ENABLED),
    "REG_WS_DAY4_PRD2_START_H": lambda unit: get_reg(unit, RegisterConstants.REG_WS_DAY4_PRD2_START_H),
    "REG_WS_DAY4_PRD2_START_M": lambda unit: get_reg(unit, RegisterConstants.REG_WS_DAY4_PRD2_START_M),
    "REG_WS_DAY4_PRD2_END_H": lambda unit: get_reg(unit, RegisterConstants.REG_WS_DAY4_PRD2_END_H),
    "REG_WS_DAY4_PRD2_END_M": lambda unit: get_reg(unit, RegisterConstants.REG_WS_DAY4_PRD2_END_M),
    "REG_WS_DAY4_PRD2_ENABLED": lambda unit: get_reg(unit, RegisterConstants.REG_WS_DAY4_PRD2_ENABLED),
    "REG_WS_DAY5_PRD1_START_H": lambda unit: get_reg(unit, RegisterConstants.REG_WS_DAY5_PRD1_START_H),
    "REG_WS_DAY5_PRD1_START_M": lambda unit: get_reg(unit, RegisterConstants.REG_WS_DAY5_PRD1_START_M),
    "REG_WS_DAY5_PRD1_END_H": lambda unit: get_reg(unit, RegisterConstants.REG_WS_DAY5_PRD1_END_H),
    "REG_WS_DAY5_PRD1_END_M": lambda unit: get_reg(unit, RegisterConstants.REG_WS_DAY5_PRD1_END_M),
    "REG_WS_DAY5_PRD1_ENABLED": lambda unit: get_reg(unit, RegisterConstants.REG_WS_DAY5_PRD1_ENABLED),
    "REG_WS_DAY5_PRD2_START_H": lambda unit: get_reg(unit, RegisterConstants.REG_WS_DAY5_PRD2_START_H),
    "REG_WS_DAY5_PRD2_START_M": lambda unit: get_reg(unit, RegisterConstants.REG_WS_DAY5_PRD2_START_M),
    "REG_WS_DAY5_PRD2_END_H": lambda unit: get_reg(unit, RegisterConstants.REG_WS_DAY5_PRD2_END_H),
    "REG_WS_DAY5_PRD2_END_M": lambda unit: get_reg(unit, RegisterConstants.REG_WS_DAY5_PRD2_END_M),
    "REG_WS_DAY5_PRD2_ENABLED": lambda unit: get_reg(unit, RegisterConstants.REG_WS_DAY5_PRD2_ENABLED),
    "REG_WS_DAY6_PRD1_START_H": lambda unit: get_reg(unit, RegisterConstants.REG_WS_DAY6_PRD1_START_H),
    "REG_WS_DAY6_PRD1_START_M": lambda unit: get_reg(unit, RegisterConstants.REG_WS_DAY6_PRD1_START_M),
    "REG_WS_DAY6_PRD1_END_H": lambda unit: get_reg(unit, RegisterConstants.REG_WS_DAY6_PRD1_END_H),
    "REG_WS_DAY6_PRD1_END_M": lambda unit: get_reg(unit, RegisterConstants.REG_WS_DAY6_PRD1_END_M),
    "REG_WS_DAY6_PRD1_ENABLED": lambda unit: get_reg(unit, RegisterConstants.REG_WS_DAY6_PRD1_ENABLED),
    "REG_WS_DAY6_PRD2_START_H": lambda unit: get_reg(unit, RegisterConstants.REG_WS_DAY6_PRD2_START_H),
    "REG_WS_DAY6_PRD2_START_M": lambda unit: get_reg(unit, RegisterConstants.REG_WS_DAY6_PRD2_START_M),
    "REG_WS_DAY6_PRD2_END_H": lambda unit: get_reg(unit, RegisterConstants.REG_WS_DAY6_PRD2_END_H),
    "REG_WS_DAY6_PRD2_END_M": lambda unit: get_reg(unit, RegisterConstants.REG_WS_DAY6_PRD2_END_M),
    "REG_WS_DAY6_PRD2_ENABLED": lambda unit: get_reg(unit, RegisterConstants.REG_WS_DAY6_PRD2_ENABLED),
    "REG_WS_DAY7_PRD1_START_H": lambda unit: get_reg(unit, RegisterConstants.REG_WS_DAY7_PRD1_START_H),
    "REG_WS_DAY7_PRD1_START_M": lambda unit: get_reg(unit, RegisterConstants.REG_WS_DAY7_PRD1_START_M),
    "REG_WS_DAY7_PRD1_END_H": lambda unit: get_reg(unit, RegisterConstants.REG_WS_DAY7_PRD1_END_H),
    "REG_WS_DAY7_PRD1_END_M": lambda unit: get_reg(unit, RegisterConstants.REG_WS_DAY7_PRD1_END_M),
    "REG_WS_DAY7_PRD1_ENABLED": lambda unit: get_reg(unit, RegisterConstants.REG_WS_DAY7_PRD1_ENABLED),
    "REG_WS_DAY7_PRD2_START_H": lambda unit: get_reg(unit, RegisterConstants.REG_WS_DAY7_PRD2_START_H),
    "REG_WS_DAY7_PRD2_START_M": lambda unit: get_reg(unit, RegisterConstants.REG_WS_DAY7_PRD2_START_M),
    "REG_WS_DAY7_PRD2_END_H": lambda unit: get_reg(unit, RegisterConstants.REG_WS_DAY7_PRD2_END_H),
    "REG_WS_DAY7_PRD2_END_M": lambda unit: get_reg(unit, RegisterConstants.REG_WS_DAY7_PRD2_END_M),
    "REG_WS_DAY7_PRD2_ENABLED": lambda unit: get_reg(unit, RegisterConstants.REG_WS_DAY7_PRD2_ENABLED),
    "REG_WS_FAN_LEVEL_SCHEDULED": lambda unit: get_reg(unit, RegisterConstants.REG_WS_FAN_LEVEL_SCHEDULED),
    "REG_WS_FAN_LEVEL_UNSCHEDULED": lambda unit: get_reg(unit, RegisterConstants.REG_WS_FAN_LEVEL_UNSCHEDULED),
    # Settings - Demand Control
    "REG_MAINBOARD_DEMC_CO2_SETTINGS_SP": lambda unit: get_reg(unit, RegisterConstants.REG_MAINBOARD_DEMC_CO2_SETTINGS_SP),
    "REG_MAINBOARD_DEMC_CO2_SETTINGS_PBAND": lambda unit: get_reg(unit, RegisterConstants.REG_MAINBOARD_DEMC_CO2_SETTINGS_PBAND),
    "REG_MAINBOARD_DEMC_CO2_SETTINGS_ITIME": lambda unit: get_reg(unit, RegisterConstants.REG_MAINBOARD_DEMC_CO2_SETTINGS_ITIME),
    "REG_MAINBOARD_DEMC_RH_SETTINGS_SP_SUMMER": lambda unit: get_reg(unit, RegisterConstants.REG_MAINBOARD_DEMC_RH_SETTINGS_SP_SUMMER),
    "REG_MAINBOARD_DEMC_RH_SETTINGS_SP_WINTER": lambda unit: get_reg(unit, RegisterConstants.REG_MAINBOARD_DEMC_RH_SETTINGS_SP_WINTER),
    "REG_MAINBOARD_DEMC_RH_SETTINGS_PBAND": lambda unit: get_reg(unit, RegisterConstants.REG_MAINBOARD_DEMC_RH_SETTINGS_PBAND),
    "REG_MAINBOARD_DEMC_RH_SETTINGS_ITIME": lambda unit: get_reg(unit, RegisterConstants.REG_MAINBOARD_DEMC_RH_SETTINGS_ITIME),
    "REG_DEMC_CO2_SETTINGS_PBAND": lambda unit: get_reg(unit, RegisterConstants.REG_DEMC_CO2_SETTINGS_PBAND),
    "REG_DEMC_CO2_SETTINGS_ITIME": lambda unit: get_reg(unit, RegisterConstants.REG_DEMC_CO2_SETTINGS_ITIME),
    "REG_DEMC_CO2_SETTINGS_SP": lambda unit: get_reg(unit, RegisterConstants.REG_DEMC_CO2_SETTINGS_SP),
    "REG_DEMC_CO2_SETTINGS_ON_OFF": lambda unit: get_reg(unit, RegisterConstants.REG_DEMC_CO2_SETTINGS_ON_OFF),
    "REG_DEMC_RH_SETTINGS_PBAND": lambda unit: get_reg(unit, RegisterConstants.REG_DEMC_RH_SETTINGS_PBAND),
    "REG_DEMC_RH_SETTINGS_ITIME": lambda unit: get_reg(unit, RegisterConstants.REG_DEMC_RH_SETTINGS_ITIME),
    "REG_DEMC_RH_SETTINGS_SP_SUMMER": lambda unit: get_reg(unit, RegisterConstants.REG_DEMC_RH_SETTINGS_SP_SUMMER),
    "REG_DEMC_RH_SETTINGS_SP_WINTER": lambda unit: get_reg(unit, RegisterConstants.REG_DEMC_RH_SETTINGS_SP_WINTER),
    "REG_DEMC_RH_SETTINGS_ON_OFF": lambda unit: get_reg(unit, RegisterConstants.REG_DEMC_RH_SETTINGS_ON_OFF),
    # Settings - Free Cooling
    "REG_MAINBOARD_FREE_COOLING_ON_OFF": lambda unit: get_reg(unit, RegisterConstants.REG_MAINBOARD_FREE_COOLING_ON_OFF),
    "REG_MAINBOARD_FREE_COOLING_MIN_SPEED_LEVEL_SAF": lambda unit: get_reg(
        unit, RegisterConstants.REG_MAINBOARD_FREE_COOLING_MIN_SPEED_LEVEL_SAF
    ),
    "REG_MAINBOARD_FREE_COOLING_MIN_SPEED_LEVEL_EAF": lambda unit: get_reg(
        unit, RegisterConstants.REG_MAINBOARD_FREE_COOLING_MIN_SPEED_LEVEL_EAF
    ),
    "REG_MAINBOARD_FREE_COOLING_START_TIME_H": lambda unit: get_reg(unit, RegisterConstants.REG_MAINBOARD_FREE_COOLING_START_TIME_H),
    "REG_MAINBOARD_FREE_COOLING_END_TIME_H": lambda unit: get_reg(unit, RegisterConstants.REG_MAINBOARD_FREE_COOLING_END_TIME_H),
    "REG_MAINBOARD_FREE_COOLING_ROOM_CANCEL_T": lambda unit: get_reg(unit, RegisterConstants.REG_MAINBOARD_FREE_COOLING_ROOM_CANCEL_T),
    "REG_MAINBOARD_FREE_COOLING_OUTDOOR_NIGHTTIME_DEACTIVATION_HIGH_T_LIMIT": lambda unit: get_reg(
        unit, RegisterConstants.REG_MAINBOARD_FREE_COOLING_OUTDOOR_NIGHTTIME_DEACTIVATION_HIGH_T_LIMIT
    ),
    "REG_MAINBOARD_FREE_COOLING_OUTDOOR_NIGHTTIME_DEACTIVATION_LOW_T_LIMIT": lambda unit: get_reg(
        unit, RegisterConstants.REG_MAINBOARD_FREE_COOLING_OUTDOOR_NIGHTTIME_DEACTIVATION_LOW_T_LIMIT
    ),
    "REG_FREE_COOLING_ON_OFF": lambda unit: get_reg(unit, RegisterConstants.REG_FREE_COOLING_ON_OFF),
    "REG_FREE_COOLING_OUTDOOR_DAYTIME_T": lambda unit: get_reg(unit, RegisterConstants.REG_FREE_COOLING_OUTDOOR_DAYTIME_T),
    "REG_FREE_COOLING_OUTDOOR_NIGHTTIME_DEACTIVATION_HIGH_T_LIMIT": lambda unit: get_reg(
        unit, RegisterConstants.REG_FREE_COOLING_OUTDOOR_NIGHTTIME_DEACTIVATION_HIGH_T_LIMIT
    ),
    "REG_FREE_COOLING_OUTDOOR_NIGHTTIME_DEACTIVATION_LOW_T_LIMIT": lambda unit: get_reg(
        unit, RegisterConstants.REG_FREE_COOLING_OUTDOOR_NIGHTTIME_DEACTIVATION_LOW_T_LIMIT
    ),
    "REG_FREE_COOLING_ROOM_CANCEL_T": lambda unit: get_reg(unit, RegisterConstants.REG_FREE_COOLING_ROOM_CANCEL_T),
    "REG_FREE_COOLING_START_TIME_H": lambda unit: get_reg(unit, RegisterConstants.REG_FREE_COOLING_START_TIME_H),
    "REG_FREE_COOLING_START_TIME_M": lambda unit: get_reg(unit, RegisterConstants.REG_FREE_COOLING_START_TIME_M),
    "REG_FREE_COOLING_END_TIME_H": lambda unit: get_reg(unit, RegisterConstants.REG_FREE_COOLING_END_TIME_H),
    "REG_FREE_COOLING_END_TIME_M": lambda unit: get_reg(unit, RegisterConstants.REG_FREE_COOLING_END_TIME_M),
    "REG_FREE_COOLING_MIN_SPEED_LEVEL_SAF": lambda unit: get_reg(unit, RegisterConstants.REG_FREE_COOLING_MIN_SPEED_LEVEL_SAF),
    "REG_FREE_COOLING_MIN_SPEED_LEVEL_EAF": lambda unit: get_reg(unit, RegisterConstants.REG_FREE_COOLING_MIN_SPEED_LEVEL_EAF),
    # Settings - Fan Config
    "REG_MAINBOARD_FAN_LEVEL_SAF_MIN": lambda unit: get_reg(unit, RegisterConstants.REG_MAINBOARD_FAN_LEVEL_SAF_MIN),
    "REG_MAINBOARD_FAN_LEVEL_EAF_MIN": lambda unit: get_reg(unit, RegisterConstants.REG_MAINBOARD_FAN_LEVEL_EAF_MIN),
    "REG_MAINBOARD_FAN_LEVEL_SAF_MIN_PERCENTAGE": lambda unit: get_reg(unit, RegisterConstants.REG_MAINBOARD_FAN_LEVEL_SAF_MIN_PERCENTAGE),
    "REG_MAINBOARD_FAN_LEVEL_EAF_MIN_PERCENTAGE": lambda unit: get_reg(unit, RegisterConstants.REG_MAINBOARD_FAN_LEVEL_EAF_MIN_PERCENTAGE),
    "REG_MAINBOARD_FAN_LEVEL_SAF_MIN_RPM": lambda unit: get_reg(unit, RegisterConstants.REG_MAINBOARD_FAN_LEVEL_SAF_MIN_RPM),
    "REG_MAINBOARD_FAN_LEVEL_EAF_MIN_RPM": lambda unit: get_reg(unit, RegisterConstants.REG_MAINBOARD_FAN_LEVEL_EAF_MIN_RPM),
    "REG_MAINBOARD_FAN_LEVEL_SAF_MIN_PRESSURE": lambda unit: get_reg(unit, RegisterConstants.REG_MAINBOARD_FAN_LEVEL_SAF_MIN_PRESSURE),
    "REG_MAINBOARD_FAN_LEVEL_EAF_MIN_PRESSURE": lambda unit: get_reg(unit, RegisterConstants.REG_MAINBOARD_FAN_LEVEL_EAF_MIN_PRESSURE),
    "REG_MAINBOARD_FAN_LEVEL_SAF_MIN_FLOW": lambda unit: get_reg(unit, RegisterConstants.REG_MAINBOARD_FAN_LEVEL_SAF_MIN_FLOW),
    "REG_MAINBOARD_FAN_LEVEL_EAF_MIN_FLOW": lambda unit: get_reg(unit, RegisterConstants.REG_MAINBOARD_FAN_LEVEL_EAF_MIN_FLOW),
    "REG_MAINBOARD_FAN_LEVEL_SAF_LOW": lambda unit: get_reg(unit, RegisterConstants.REG_MAINBOARD_FAN_LEVEL_SAF_LOW),
    "REG_MAINBOARD_FAN_LEVEL_EAF_LOW": lambda unit: get_reg(unit, RegisterConstants.REG_MAINBOARD_FAN_LEVEL_EAF_LOW),
    "REG_MAINBOARD_FAN_LEVEL_SAF_LOW_PERCENTAGE": lambda unit: get_reg(unit, RegisterConstants.REG_MAINBOARD_FAN_LEVEL_SAF_LOW_PERCENTAGE),
    "REG_MAINBOARD_FAN_LEVEL_EAF_LOW_PERCENTAGE": lambda unit: get_reg(unit, RegisterConstants.REG_MAINBOARD_FAN_LEVEL_EAF_LOW_PERCENTAGE),
    "REG_MAINBOARD_FAN_LEVEL_SAF_LOW_RPM": lambda unit: get_reg(unit, RegisterConstants.REG_MAINBOARD_FAN_LEVEL_SAF_LOW_RPM),
    "REG_MAINBOARD_FAN_LEVEL_EAF_LOW_RPM": lambda unit: get_reg(unit, RegisterConstants.REG_MAINBOARD_FAN_LEVEL_EAF_LOW_RPM),
    "REG_MAINBOARD_FAN_LEVEL_SAF_LOW_PRESSURE": lambda unit: get_reg(unit, RegisterConstants.REG_MAINBOARD_FAN_LEVEL_SAF_LOW_PRESSURE),
    "REG_MAINBOARD_FAN_LEVEL_EAF_LOW_PRESSURE": lambda unit: get_reg(unit, RegisterConstants.REG_MAINBOARD_FAN_LEVEL_EAF_LOW_PRESSURE),
    "REG_MAINBOARD_FAN_LEVEL_SAF_LOW_FLOW": lambda unit: get_reg(unit, RegisterConstants.REG_MAINBOARD_FAN_LEVEL_SAF_LOW_FLOW),
    "REG_MAINBOARD_FAN_LEVEL_EAF_LOW_FLOW": lambda unit: get_reg(unit, RegisterConstants.REG_MAINBOARD_FAN_LEVEL_EAF_LOW_FLOW),
    "REG_MAINBOARD_FAN_LEVEL_SAF_NORMAL": lambda unit: get_reg(unit, RegisterConstants.REG_MAINBOARD_FAN_LEVEL_SAF_NORMAL),
    "REG_MAINBOARD_FAN_LEVEL_EAF_NORMAL": lambda unit: get_reg(unit, RegisterConstants.REG_MAINBOARD_FAN_LEVEL_EAF_NORMAL),
    "REG_MAINBOARD_FAN_LEVEL_SAF_NORMAL_PERCENTAGE": lambda unit: get_reg(
        unit, RegisterConstants.REG_MAINBOARD_FAN_LEVEL_SAF_NORMAL_PERCENTAGE
    ),
    "REG_MAINBOARD_FAN_LEVEL_EAF_NORMAL_PERCENTAGE": lambda unit: get_reg(
        unit, RegisterConstants.REG_MAINBOARD_FAN_LEVEL_EAF_NORMAL_PERCENTAGE
    ),
    "REG_MAINBOARD_FAN_LEVEL_SAF_NORMAL_RPM": lambda unit: get_reg(unit, RegisterConstants.REG_MAINBOARD_FAN_LEVEL_SAF_NORMAL_RPM),
    "REG_MAINBOARD_FAN_LEVEL_EAF_NORMAL_RPM": lambda unit: get_reg(unit, RegisterConstants.REG_MAINBOARD_FAN_LEVEL_EAF_NORMAL_RPM),
    "REG_MAINBOARD_FAN_LEVEL_SAF_NORMAL_PRESSURE": lambda unit: get_reg(
        unit, RegisterConstants.REG_MAINBOARD_FAN_LEVEL_SAF_NORMAL_PRESSURE
    ),
    "REG_MAINBOARD_FAN_LEVEL_EAF_NORMAL_PRESSURE": lambda unit: get_reg(
        unit, RegisterConstants.REG_MAINBOARD_FAN_LEVEL_EAF_NORMAL_PRESSURE
    ),
    "REG_MAINBOARD_FAN_LEVEL_SAF_NORMAL_FLOW": lambda unit: get_reg(unit, RegisterConstants.REG_MAINBOARD_FAN_LEVEL_SAF_NORMAL_FLOW),
    "REG_MAINBOARD_FAN_LEVEL_EAF_NORMAL_FLOW": lambda unit: get_reg(unit, RegisterConstants.REG_MAINBOARD_FAN_LEVEL_EAF_NORMAL_FLOW),
    "REG_MAINBOARD_FAN_LEVEL_SAF_HIGH": lambda unit: get_reg(unit, RegisterConstants.REG_MAINBOARD_FAN_LEVEL_SAF_HIGH),
    "REG_MAINBOARD_FAN_LEVEL_EAF_HIGH": lambda unit: get_reg(unit, RegisterConstants.REG_MAINBOARD_FAN_LEVEL_EAF_HIGH),
    "REG_MAINBOARD_FAN_LEVEL_SAF_HIGH_PERCENTAGE": lambda unit: get_reg(
        unit, RegisterConstants.REG_MAINBOARD_FAN_LEVEL_SAF_HIGH_PERCENTAGE
    ),
    "REG_MAINBOARD_FAN_LEVEL_EAF_HIGH_PERCENTAGE": lambda unit: get_reg(
        unit, RegisterConstants.REG_MAINBOARD_FAN_LEVEL_EAF_HIGH_PERCENTAGE
    ),
    "REG_MAINBOARD_FAN_LEVEL_SAF_HIGH_RPM": lambda unit: get_reg(unit, RegisterConstants.REG_MAINBOARD_FAN_LEVEL_SAF_HIGH_RPM),
    "REG_MAINBOARD_FAN_LEVEL_EAF_HIGH_RPM": lambda unit: get_reg(unit, RegisterConstants.REG_MAINBOARD_FAN_LEVEL_EAF_HIGH_RPM),
    "REG_MAINBOARD_FAN_LEVEL_SAF_HIGH_PRESSURE": lambda unit: get_reg(unit, RegisterConstants.REG_MAINBOARD_FAN_LEVEL_SAF_HIGH_PRESSURE),
    "REG_MAINBOARD_FAN_LEVEL_EAF_HIGH_PRESSURE": lambda unit: get_reg(unit, RegisterConstants.REG_MAINBOARD_FAN_LEVEL_EAF_HIGH_PRESSURE),
    "REG_MAINBOARD_FAN_LEVEL_SAF_HIGH_FLOW": lambda unit: get_reg(unit, RegisterConstants.REG_MAINBOARD_FAN_LEVEL_SAF_HIGH_FLOW),
    "REG_MAINBOARD_FAN_LEVEL_EAF_HIGH_FLOW": lambda unit: get_reg(unit, RegisterConstants.REG_MAINBOARD_FAN_LEVEL_EAF_HIGH_FLOW),
    "REG_MAINBOARD_FAN_LEVEL_SAF_MAX": lambda unit: get_reg(unit, RegisterConstants.REG_MAINBOARD_FAN_LEVEL_SAF_MAX),
    "REG_MAINBOARD_FAN_LEVEL_EAF_MAX": lambda unit: get_reg(unit, RegisterConstants.REG_MAINBOARD_FAN_LEVEL_EAF_MAX),
    "REG_MAINBOARD_FAN_LEVEL_SAF_MAX_PERCENTAGE": lambda unit: get_reg(unit, RegisterConstants.REG_MAINBOARD_FAN_LEVEL_SAF_MAX_PERCENTAGE),
    "REG_MAINBOARD_FAN_LEVEL_EAF_MAX_PERCENTAGE": lambda unit: get_reg(unit, RegisterConstants.REG_MAINBOARD_FAN_LEVEL_EAF_MAX_PERCENTAGE),
    "REG_MAINBOARD_FAN_LEVEL_SAF_MAX_RPM": lambda unit: get_reg(unit, RegisterConstants.REG_MAINBOARD_FAN_LEVEL_SAF_MAX_RPM),
    "REG_MAINBOARD_FAN_LEVEL_EAF_MAX_RPM": lambda unit: get_reg(unit, RegisterConstants.REG_MAINBOARD_FAN_LEVEL_EAF_MAX_RPM),
    "REG_MAINBOARD_FAN_LEVEL_SAF_MAX_PRESSURE": lambda unit: get_reg(unit, RegisterConstants.REG_MAINBOARD_FAN_LEVEL_SAF_MAX_PRESSURE),
    "REG_MAINBOARD_FAN_LEVEL_EAF_MAX_PRESSURE": lambda unit: get_reg(unit, RegisterConstants.REG_MAINBOARD_FAN_LEVEL_EAF_MAX_PRESSURE),
    "REG_MAINBOARD_FAN_LEVEL_SAF_MAX_FLOW": lambda unit: get_reg(unit, RegisterConstants.REG_MAINBOARD_FAN_LEVEL_SAF_MAX_FLOW),
    "REG_MAINBOARD_FAN_LEVEL_EAF_MAX_FLOW": lambda unit: get_reg(unit, RegisterConstants.REG_MAINBOARD_FAN_LEVEL_EAF_MAX_FLOW),
    "REG_MAINBOARD_FAN_REGULATION_UNIT": lambda unit: get_reg(unit, RegisterConstants.REG_MAINBOARD_FAN_REGULATION_UNIT),
    "REG_FAN_REGULATION_UNIT": lambda unit: get_reg(unit, RegisterConstants.REG_FAN_REGULATION_UNIT),
    "REG_FAN_LEVEL_SAF_MIN_PERCENTAGE": lambda unit: get_reg(unit, RegisterConstants.REG_FAN_LEVEL_SAF_MIN_PERCENTAGE),
    "REG_FAN_LEVEL_EAF_MIN_PERCENTAGE": lambda unit: get_reg(unit, RegisterConstants.REG_FAN_LEVEL_EAF_MIN_PERCENTAGE),
    "REG_FAN_LEVEL_SAF_MIN_RPM": lambda unit: get_reg(unit, RegisterConstants.REG_FAN_LEVEL_SAF_MIN_RPM),
    "REG_FAN_LEVEL_EAF_MIN_RPM": lambda unit: get_reg(unit, RegisterConstants.REG_FAN_LEVEL_EAF_MIN_RPM),
    "REG_FAN_LEVEL_SAF_MIN_PRESSURE": lambda unit: get_reg(unit, RegisterConstants.REG_FAN_LEVEL_SAF_MIN_PRESSURE),
    "REG_FAN_LEVEL_EAF_MIN_PRESSURE": lambda unit: get_reg(unit, RegisterConstants.REG_FAN_LEVEL_EAF_MIN_PRESSURE),
    "REG_FAN_LEVEL_SAF_MIN_FLOW": lambda unit: get_reg(unit, RegisterConstants.REG_FAN_LEVEL_SAF_MIN_FLOW),
    "REG_FAN_LEVEL_EAF_MIN_FLOW": lambda unit: get_reg(unit, RegisterConstants.REG_FAN_LEVEL_EAF_MIN_FLOW),
    "REG_FAN_LEVEL_SAF_LOW_PERCENTAGE": lambda unit: get_reg(unit, RegisterConstants.REG_FAN_LEVEL_SAF_LOW_PERCENTAGE),
    "REG_FAN_LEVEL_EAF_LOW_PERCENTAGE": lambda unit: get_reg(unit, RegisterConstants.REG_FAN_LEVEL_EAF_LOW_PERCENTAGE),
    "REG_FAN_LEVEL_SAF_LOW_RPM": lambda unit: get_reg(unit, RegisterConstants.REG_FAN_LEVEL_SAF_LOW_RPM),
    "REG_FAN_LEVEL_EAF_LOW_RPM": lambda unit: get_reg(unit, RegisterConstants.REG_FAN_LEVEL_EAF_LOW_RPM),
    "REG_FAN_LEVEL_SAF_LOW_PRESSURE": lambda unit: get_reg(unit, RegisterConstants.REG_FAN_LEVEL_SAF_LOW_PRESSURE),
    "REG_FAN_LEVEL_EAF_LOW_PRESSURE": lambda unit: get_reg(unit, RegisterConstants.REG_FAN_LEVEL_EAF_LOW_PRESSURE),
    "REG_FAN_LEVEL_SAF_LOW_FLOW": lambda unit: get_reg(unit, RegisterConstants.REG_FAN_LEVEL_SAF_LOW_FLOW),
    "REG_FAN_LEVEL_EAF_LOW_FLOW": lambda unit: get_reg(unit, RegisterConstants.REG_FAN_LEVEL_EAF_LOW_FLOW),
    "REG_FAN_LEVEL_SAF_NORMAL_PERCENTAGE": lambda unit: get_reg(unit, RegisterConstants.REG_FAN_LEVEL_SAF_NORMAL_PERCENTAGE),
    "REG_FAN_LEVEL_EAF_NORMAL_PERCENTAGE": lambda unit: get_reg(unit, RegisterConstants.REG_FAN_LEVEL_EAF_NORMAL_PERCENTAGE),
    "REG_FAN_LEVEL_SAF_NORMAL_RPM": lambda unit: get_reg(unit, RegisterConstants.REG_FAN_LEVEL_SAF_NORMAL_RPM),
    "REG_FAN_LEVEL_EAF_NORMAL_RPM": lambda unit: get_reg(unit, RegisterConstants.REG_FAN_LEVEL_EAF_NORMAL_RPM),
    "REG_FAN_LEVEL_SAF_NORMAL_PRESSURE": lambda unit: get_reg(unit, RegisterConstants.REG_FAN_LEVEL_SAF_NORMAL_PRESSURE),
    "REG_FAN_LEVEL_EAF_NORMAL_PRESSURE": lambda unit: get_reg(unit, RegisterConstants.REG_FAN_LEVEL_EAF_NORMAL_PRESSURE),
    "REG_FAN_LEVEL_SAF_NORMAL_FLOW": lambda unit: get_reg(unit, RegisterConstants.REG_FAN_LEVEL_SAF_NORMAL_FLOW),
    "REG_FAN_LEVEL_EAF_NORMAL_FLOW": lambda unit: get_reg(unit, RegisterConstants.REG_FAN_LEVEL_EAF_NORMAL_FLOW),
    "REG_FAN_LEVEL_SAF_HIGH_PERCENTAGE": lambda unit: get_reg(unit, RegisterConstants.REG_FAN_LEVEL_SAF_HIGH_PERCENTAGE),
    "REG_FAN_LEVEL_EAF_HIGH_PERCENTAGE": lambda unit: get_reg(unit, RegisterConstants.REG_FAN_LEVEL_EAF_HIGH_PERCENTAGE),
    "REG_FAN_LEVEL_SAF_HIGH_RPM": lambda unit: get_reg(unit, RegisterConstants.REG_FAN_LEVEL_SAF_HIGH_RPM),
    "REG_FAN_LEVEL_EAF_HIGH_RPM": lambda unit: get_reg(unit, RegisterConstants.REG_FAN_LEVEL_EAF_HIGH_RPM),
    "REG_FAN_LEVEL_SAF_HIGH_PRESSURE": lambda unit: get_reg(unit, RegisterConstants.REG_FAN_LEVEL_SAF_HIGH_PRESSURE),
    "REG_FAN_LEVEL_EAF_HIGH_PRESSURE": lambda unit: get_reg(unit, RegisterConstants.REG_FAN_LEVEL_EAF_HIGH_PRESSURE),
    "REG_FAN_LEVEL_SAF_HIGH_FLOW": lambda unit: get_reg(unit, RegisterConstants.REG_FAN_LEVEL_SAF_HIGH_FLOW),
    "REG_FAN_LEVEL_EAF_HIGH_FLOW": lambda unit: get_reg(unit, RegisterConstants.REG_FAN_LEVEL_EAF_HIGH_FLOW),
    "REG_FAN_LEVEL_SAF_MAX_PERCENTAGE": lambda unit: get_reg(unit, RegisterConstants.REG_FAN_LEVEL_SAF_MAX_PERCENTAGE),
    "REG_FAN_LEVEL_EAF_MAX_PERCENTAGE": lambda unit: get_reg(unit, RegisterConstants.REG_FAN_LEVEL_EAF_MAX_PERCENTAGE),
    "REG_FAN_LEVEL_SAF_MAX_RPM": lambda unit: get_reg(unit, RegisterConstants.REG_FAN_LEVEL_SAF_MAX_RPM),
    "REG_FAN_LEVEL_EAF_MAX_RPM": lambda unit: get_reg(unit, RegisterConstants.REG_FAN_LEVEL_EAF_MAX_RPM),
    "REG_FAN_LEVEL_SAF_MAX_PRESSURE": lambda unit: get_reg(unit, RegisterConstants.REG_FAN_LEVEL_SAF_MAX_PRESSURE),
    "REG_FAN_LEVEL_EAF_MAX_PRESSURE": lambda unit: get_reg(unit, RegisterConstants.REG_FAN_LEVEL_EAF_MAX_PRESSURE),
    "REG_FAN_LEVEL_SAF_MAX_FLOW": lambda unit: get_reg(unit, RegisterConstants.REG_FAN_LEVEL_SAF_MAX_FLOW),
    "REG_FAN_LEVEL_EAF_MAX_FLOW": lambda unit: get_reg(unit, RegisterConstants.REG_FAN_LEVEL_EAF_MAX_FLOW),
    # Unit Config
    "REG_MAINBOARD_HEAT_EXCHANGER_TYPE": lambda unit: get_reg(unit, RegisterConstants.REG_MAINBOARD_HEAT_EXCHANGER_TYPE),
    "REG_MAINBOARD_UNIT_CONFIG_REHEATER_TYPE": lambda unit: get_reg(unit, RegisterConstants.REG_MAINBOARD_UNIT_CONFIG_REHEATER_TYPE),
    "REG_MAINBOARD_UNIT_CONFIG_BYPASS_LOCATION": lambda unit: get_reg(unit, RegisterConstants.REG_MAINBOARD_UNIT_CONFIG_BYPASS_LOCATION),
    "REG_MAINBOARD_DEFROSTING_DISABLE": lambda unit: get_reg(unit, RegisterConstants.REG_MAINBOARD_DEFROSTING_DISABLE),
    "REG_MAINBOARD_CFG_HEAT_EXCHANGER_ACTUATOR_TYPE": lambda unit: get_reg(
        unit, RegisterConstants.REG_MAINBOARD_CFG_HEAT_EXCHANGER_ACTUATOR_TYPE
    ),
    "REG_MAINBOARD_PASSIVE_HOUSE_ACTIVATION": lambda unit: get_reg(unit, RegisterConstants.REG_MAINBOARD_PASSIVE_HOUSE_ACTIVATION),
    "REG_MAINBOARD_PASSIVE_HOUSE_CERTIFICATION": lambda unit: get_reg(unit, RegisterConstants.REG_MAINBOARD_PASSIVE_HOUSE_CERTIFICATION),
    "REG_MAINBOARD_PASSIVE_HOUSE_MAX_LIMIT": lambda unit: get_reg(unit, RegisterConstants.REG_MAINBOARD_PASSIVE_HOUSE_MAX_LIMIT),
    "REG_MAINBOARD_CFG_HEATER_ACTUATOR_TYPE": lambda unit: get_reg(unit, RegisterConstants.REG_MAINBOARD_CFG_HEATER_ACTUATOR_TYPE),
    "REG_MAINBOARD_CFG_CHANGE_OVER_ACTUATOR_TYPE": lambda unit: get_reg(
        unit, RegisterConstants.REG_MAINBOARD_CFG_CHANGE_OVER_ACTUATOR_TYPE
    ),
    "REG_MAINBOARD_HEATER_CIRC_PUMP_START_T": lambda unit: get_reg(unit, RegisterConstants.REG_MAINBOARD_HEATER_CIRC_PUMP_START_T),
    "REG_MAINBOARD_HEATER_CIRC_PUMP_STOP_DELAY": lambda unit: get_reg(unit, RegisterConstants.REG_MAINBOARD_HEATER_CIRC_PUMP_STOP_DELAY),
    "REG_MAINBOARD_CHANGE_OVER_CIRC_PUMP_START_T": lambda unit: get_reg(
        unit, RegisterConstants.REG_MAINBOARD_CHANGE_OVER_CIRC_PUMP_START_T
    ),
    "REG_MAINBOARD_CHANGE_OVER_CIRC_PUMP_STOP_DELAY": lambda unit: get_reg(
        unit, RegisterConstants.REG_MAINBOARD_CHANGE_OVER_CIRC_PUMP_STOP_DELAY
    ),
    "REG_MAINBOARD_UNIT_CONFIG_COOLER": lambda unit: get_reg(unit, RegisterConstants.REG_MAINBOARD_UNIT_CONFIG_COOLER),
    "REG_MAINBOARD_CFG_COOLER_ACTUATOR_TYPE": lambda unit: get_reg(unit, RegisterConstants.REG_MAINBOARD_CFG_COOLER_ACTUATOR_TYPE),
    "REG_MAINBOARD_COOLER_OAT_INTERLOCK_T": lambda unit: get_reg(unit, RegisterConstants.REG_MAINBOARD_COOLER_OAT_INTERLOCK_T),
    "REG_MAINBOARD_COOLER_CIRC_PUMP_STOP_DELAY": lambda unit: get_reg(unit, RegisterConstants.REG_MAINBOARD_COOLER_CIRC_PUMP_STOP_DELAY),
    "REG_MAINBOARD_UNIT_CONFIG_EXTRA_CONTROLLER": lambda unit: get_reg(unit, RegisterConstants.REG_MAINBOARD_UNIT_CONFIG_EXTRA_CONTROLLER),
    "REG_UNIT_CONFIG_REHEATER_TYPE": lambda unit: get_reg(unit, RegisterConstants.REG_UNIT_CONFIG_REHEATER_TYPE),
    "REG_UNIT_CONFIG_BYPASS_LOCATION": lambda unit: get_reg(unit, RegisterConstants.REG_UNIT_CONFIG_BYPASS_LOCATION),
    "REG_UNIT_CONFIG_PREHEATER": lambda unit: get_reg(unit, RegisterConstants.REG_UNIT_CONFIG_PREHEATER),
    "REG_UNIT_CONFIG_COOLER": lambda unit: get_reg(unit, RegisterConstants.REG_UNIT_CONFIG_COOLER),
    "REG_UNIT_CONFIG_EXTRA_CONTROLLER": lambda unit: get_reg(unit, RegisterConstants.REG_UNIT_CONFIG_EXTRA_CONTROLLER),
    "REG_UNIT_CONFIG_RHS_PDM": lambda unit: get_reg(unit, RegisterConstants.REG_UNIT_CONFIG_RHS_PDM),
    "REG_UNIT_CONFIG_BYF": lambda unit: get_reg(unit, RegisterConstants.REG_UNIT_CONFIG_BYF),
    "REG_SYSTEM_UNIT_MODEL1": lambda unit: get_reg(unit, RegisterConstants.REG_SYSTEM_UNIT_MODEL1),
    "REG_SYSTEM_SERIAL_NUMBER1": lambda unit: get_reg(unit, RegisterConstants.REG_SYSTEM_SERIAL_NUMBER1),
    # IAQ
    "REG_IAQ_LEVEL": lambda unit: unit.registers.get(RegisterConstants.REG_MAINBOARD_IAQ_LEVEL, getattr(unit, "iaq_level", 0)),
    # CO2
    "REG_SENSOR_MODBUS_CO2": lambda unit: unit.registers.get(RegisterConstants.REG_MAINBOARD_SENSOR_CO2S, getattr(unit, "co2", 0)),
}

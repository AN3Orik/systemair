"""Legacy Residential / D24810 device profile."""

from __future__ import annotations

from homeassistant.const import Platform

from custom_components.systemair.const import API_TYPE_MODBUS_SERIAL, API_TYPE_MODBUS_TCP
from custom_components.systemair.modbus import IntegerType, ModbusParameter, RegisterType
from custom_components.systemair.profiles.base import DeviceProfile, ProfileEntityDescriptions


def _uint(register: int, short: str, description: str, *, min_value: int | None = None, max_value: int | None = None) -> ModbusParameter:
    return ModbusParameter(
        register=register,
        sig=IntegerType.UINT,
        reg_type=RegisterType.Holding,
        short=short,
        description=description,
        min_value=min_value,
        max_value=max_value,
    )


D24810_PARAMETERS = [
    _uint(
        101,
        "REG_FAN_SPEED_LEVEL",
        "Fans off/low/normal/high/auto mode. 0: off, 1: low, 2: normal, 3: high, 4: auto.",
        min_value=0,
        max_value=4,
    ),
    _uint(102, "REG_FAN_SAF_FLOW_LOW", "Supply air fan speed for low speed."),
    _uint(103, "REG_FAN_EAF_FLOW_LOW", "Extract air fan speed for low speed."),
    _uint(104, "REG_FAN_SAF_FLOW_NOM", "Supply air fan speed for nominal speed."),
    _uint(105, "REG_FAN_EAF_FLOW_NOM", "Extract air fan speed for nominal speed."),
    _uint(106, "REG_FAN_SAF_FLOW_HIGH", "Supply air fan speed for high speed."),
    _uint(107, "REG_FAN_EAF_FLOW_HIGH", "Extract air fan speed for high speed."),
    _uint(108, "REG_FAN_FLOW_UNITS", "Airflow unit. 0: l/s, 1: m3/h.", min_value=0, max_value=1),
    _uint(109, "REG_FAN_SAF_PWM", "Supply fan PWM output, 0..100 percent.", min_value=0, max_value=100),
    _uint(110, "REG_FAN_EAF_PWM", "Extract fan PWM output, 0..100 percent.", min_value=0, max_value=100),
    _uint(111, "REG_FAN_SAF_RPM", "Supply fan RPM indication."),
    _uint(112, "REG_FAN_EAF_RPM", "Extract fan RPM indication."),
    _uint(
        114,
        "REG_FAN_ALLOW_MANUAL_STOP",
        "Manual fan stop allowed. 0: stop not allowed, 1: stop allowed.",
        min_value=0,
        max_value=1,
    ),
    _uint(
        501,
        "REG_SYSTEM_TYPE",
        "System type. 0: VR400, 1: VR700, 2: VR700DK, 3: VR400DE, 4: VTC300, 5: VTC700, 12..21 listed residential units.",
    ),
    _uint(601, "REG_FILTER_PERIOD", "Filter replacement period in months.", min_value=1, max_value=24),
    _uint(602, "REG_FILTER_DAYS", "Elapsed days since last filter replacement.", min_value=0, max_value=3650),
]

d24810_parameter_map = {param.short: param for param in D24810_PARAMETERS}

D24810_PROFILE = DeviceProfile(
    profile_id="legacy_d24810",
    name="Legacy Residential / D24810",
    supported_api_types=(API_TYPE_MODBUS_TCP, API_TYPE_MODBUS_SERIAL),
    supported_platforms=(
        Platform.CLIMATE,
        Platform.SENSOR,
        Platform.BINARY_SENSOR,
        Platform.SWITCH,
        Platform.NUMBER,
        Platform.SELECT,
    ),
    registry=d24810_parameter_map,
    read_blocks=((101, 14), (501, 1), (601, 2)),
    test_register=501,
    model_options=(
        "VR400",
        "VR700",
        "VR700DK",
        "VR400DE",
        "VTC300",
        "VTC700",
        "VTR150K",
        "VTR200B",
        "VSR300",
        "VSR500",
        "VSR150",
        "VTR300",
        "VTR500",
        "VSR300DE",
        "VTC200",
        "VTC100",
    ),
    entities=ProfileEntityDescriptions(),
)

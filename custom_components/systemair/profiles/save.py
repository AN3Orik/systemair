"""SAVE device profile."""

from __future__ import annotations

from homeassistant.const import Platform

from custom_components.systemair.const import (
    API_TYPE_HOMESOLUTION,
    API_TYPE_MODBUS_SERIAL,
    API_TYPE_MODBUS_TCP,
    API_TYPE_MODBUS_WEBAPI,
    MODEL_SPECS,
)
from custom_components.systemair.modbus import parameter_map
from custom_components.systemair.profiles.base import DeviceProfile

SAVE_READ_BLOCKS_BASE = (
    (1001, 62),
    (1101, 88),
    (1201, 74),
    (1351, 3),
    (1410, 10),
    (2001, 125),
    (2126, 24),
    (2201, 63),
    (2311, 8),
    (2401, 53),
    (2504, 18),
    (3002, 116),
    (4001, 12),
    (4101, 20),
    (7001, 6),
    (12011, 2),
    (12101, 41),
    (12301, 17),
    (12401, 5),
    (12544, 1),
    (14001, 4),
    (14101, 5),
    (14201, 4),
    (14301, 11),
    (14381, 1),
    (15901, 10),
)

SAVE_READ_BLOCKS_ALARM_DETAILS = (
    (15016, 125),
    (15141, 125),
    (15266, 125),
    (15391, 125),
    (15516, 125),
)

SAVE_READ_BLOCKS_ALARM_HISTORY = (
    (15641, 125),
    (15766, 125),
    (15891, 10),
)

SAVE_PROFILE = DeviceProfile(
    profile_id="save",
    name="SAVE",
    supported_api_types=(API_TYPE_MODBUS_TCP, API_TYPE_MODBUS_SERIAL, API_TYPE_MODBUS_WEBAPI, API_TYPE_HOMESOLUTION),
    supported_platforms=(
        Platform.BUTTON,
        Platform.CLIMATE,
        Platform.SENSOR,
        Platform.BINARY_SENSOR,
        Platform.SWITCH,
        Platform.NUMBER,
        Platform.SELECT,
    ),
    registry=parameter_map,
    read_blocks=SAVE_READ_BLOCKS_BASE,
    alarm_detail_blocks=SAVE_READ_BLOCKS_ALARM_DETAILS,
    alarm_history_blocks=SAVE_READ_BLOCKS_ALARM_HISTORY,
    test_register=parameter_map["REG_TC_SP"].register,
    model_options=tuple(MODEL_SPECS),
)

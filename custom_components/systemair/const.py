"""Constants for Systemair."""

from logging import Logger, getLogger

LOGGER: Logger = getLogger(__package__)

DOMAIN = "systemair"
ATTRIBUTION = "Data provided by Systemair SAVE Connect."

# --- Configuration Constants ---
CONF_MODEL = "model"
CONF_SLAVE_ID = "slave_id"
DEFAULT_PORT = 502
DEFAULT_SLAVE_ID = 1

# --- Power Specs for different models ---
MODEL_SPECS = {
    "VSR 300": {"fan_power": 166, "heater_power": 1670},
    "VSR 500": {"fan_power": 338, "heater_power": 1670},
    "VSR 150/B": {"fan_power": 74, "heater_power": 500},
    "VTR 200/B (500Wt Heater)": {"fan_power": 168, "heater_power": 500},
    "VTR 200/B (1000Wt Heater)": {"fan_power": 168, "heater_power": 1000},
}


# Constants from the old integration
MAX_TEMP = 30
MIN_TEMP = 12

PRESET_MODE_AUTO = "auto"
PRESET_MODE_MANUAL = "manual"
PRESET_MODE_CROWDED = "crowded"
PRESET_MODE_REFRESH = "refresh"
PRESET_MODE_FIREPLACE = "fireplace"
PRESET_MODE_AWAY = "away"
PRESET_MODE_HOLIDAY = "holiday"

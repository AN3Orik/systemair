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
    "VSC 100": {"fan_power": 27, "heater_power": 0, "supply_fans": 1, "extract_fans": 0},
    "VSC 200": {"fan_power": 81, "heater_power": 0, "supply_fans": 1, "extract_fans": 0},
    "VSC 300": {"fan_power": 115, "heater_power": 0, "supply_fans": 1, "extract_fans": 0},
    "VSR 150/B": {"fan_power": 70, "heater_power": 500, "supply_fans": 1, "extract_fans": 1},
    "VSR 150/B L": {"fan_power": 70, "heater_power": 500, "supply_fans": 1, "extract_fans": 1},
    "VSR 150/B R": {"fan_power": 70, "heater_power": 500, "supply_fans": 1, "extract_fans": 1},
    "VSR 200/B L": {"fan_power": 162, "heater_power": 1000, "supply_fans": 1, "extract_fans": 1},
    "VSR 200/B R": {"fan_power": 162, "heater_power": 1000, "supply_fans": 1, "extract_fans": 1},
    "VSR 300": {"fan_power": 166, "heater_power": 1670, "supply_fans": 1, "extract_fans": 1},
    "VSR 400": {"fan_power": 338, "heater_power": 1670, "supply_fans": 1, "extract_fans": 1},
    "VSR 500": {"fan_power": 338, "heater_power": 1670, "supply_fans": 1, "extract_fans": 1},
    "VSR 700": {"fan_power": 340, "heater_power": 1670, "supply_fans": 1, "extract_fans": 1},
    "VTC 200 L": {"fan_power": 170, "heater_power": 0, "supply_fans": 1, "extract_fans": 1},
    "VTC 200 R": {"fan_power": 170, "heater_power": 0, "supply_fans": 1, "extract_fans": 1},
    "VTC 200-1 L": {"fan_power": 162, "heater_power": 0, "supply_fans": 1, "extract_fans": 1},
    "VTC 200-1 R": {"fan_power": 162, "heater_power": 0, "supply_fans": 1, "extract_fans": 1},
    "VTC 300 L": {"fan_power": 170, "heater_power": 0, "supply_fans": 1, "extract_fans": 1},
    "VTC 300 R": {"fan_power": 170, "heater_power": 0, "supply_fans": 1, "extract_fans": 1},
    "VTC 500 L": {"fan_power": 340, "heater_power": 0, "supply_fans": 1, "extract_fans": 1},
    "VTC 500 R": {"fan_power": 340, "heater_power": 0, "supply_fans": 1, "extract_fans": 1},
    "VTC 700 L": {"fan_power": 340, "heater_power": 0, "supply_fans": 1, "extract_fans": 1},
    "VTC 700 R": {"fan_power": 340, "heater_power": 0, "supply_fans": 1, "extract_fans": 1},
    "VTR 100/B": {"fan_power": 70, "heater_power": 0, "supply_fans": 1, "extract_fans": 1},
    "VTR 150/B L 500W": {"fan_power": 166, "heater_power": 500, "supply_fans": 1, "extract_fans": 1},
    "VTR 150/B L 1000W": {"fan_power": 166, "heater_power": 1000, "supply_fans": 1, "extract_fans": 1},
    "VTR 150/B R 500W": {"fan_power": 166, "heater_power": 500, "supply_fans": 1, "extract_fans": 1},
    "VTR 150/B R 1000W": {"fan_power": 166, "heater_power": 1000, "supply_fans": 1, "extract_fans": 1},
    "VTR 150/K L 500W": {"fan_power": 172, "heater_power": 500, "supply_fans": 1, "extract_fans": 1},
    "VTR 150/K L 1000W": {"fan_power": 172, "heater_power": 1000, "supply_fans": 1, "extract_fans": 1},
    "VTR 150/K R 500W": {"fan_power": 172, "heater_power": 500, "supply_fans": 1, "extract_fans": 1},
    "VTR 150/K R 1000W": {"fan_power": 172, "heater_power": 1000, "supply_fans": 1, "extract_fans": 1},
    "VTR 250/B L 500W": {"fan_power": 162, "heater_power": 500, "supply_fans": 1, "extract_fans": 1},
    "VTR 250/B L 1000W": {"fan_power": 162, "heater_power": 1000, "supply_fans": 1, "extract_fans": 1},
    "VTR 250/B R 500W": {"fan_power": 162, "heater_power": 500, "supply_fans": 1, "extract_fans": 1},
    "VTR 250/B R 1000W": {"fan_power": 162, "heater_power": 1000, "supply_fans": 1, "extract_fans": 1},
    "VTR 275/B L": {"fan_power": 162, "heater_power": 500, "supply_fans": 1, "extract_fans": 1},
    "VTR 275/B R": {"fan_power": 162, "heater_power": 500, "supply_fans": 1, "extract_fans": 1},
    "VTR 300/B L": {"fan_power": 162, "heater_power": 1670, "supply_fans": 1, "extract_fans": 1},
    "VTR 300/B R": {"fan_power": 162, "heater_power": 1670, "supply_fans": 1, "extract_fans": 1},
    "VTR 350/B L": {"fan_power": 338, "heater_power": 1670, "supply_fans": 1, "extract_fans": 1},
    "VTR 350/B R": {"fan_power": 338, "heater_power": 1670, "supply_fans": 1, "extract_fans": 1},
    "VTR 500 L": {"fan_power": 340, "heater_power": 1670, "supply_fans": 1, "extract_fans": 1},
    "VTR 500 R": {"fan_power": 340, "heater_power": 1670, "supply_fans": 1, "extract_fans": 1},
    "VTR 700 L": {"fan_power": 340, "heater_power": 0, "supply_fans": 1, "extract_fans": 1},
    "VTR 700 R": {"fan_power": 340, "heater_power": 0, "supply_fans": 1, "extract_fans": 1},
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

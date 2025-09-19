"""Constants for Systemair."""
from logging import Logger, getLogger

LOGGER: Logger = getLogger(__package__)

DOMAIN = "systemair"
ATTRIBUTION = "Data provided by Systemair SAVE Connect."

# Constants for Modbus configuration
CONF_SLAVE_ID = "slave_id"
DEFAULT_PORT = 502
DEFAULT_SLAVE_ID = 1

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
PRESET_MODE_COOKER_HOOD = "cooker_hood"
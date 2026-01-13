"""Constants for the Systemair API, including endpoints and user modes."""

from enum import IntEnum

CLIENT_ID = "iot-application"
REDIRECT_URI = "https://homesolutions.systemair.com"
AUTH_URL = "https://sso.systemair.com/auth/realms/iot/protocol/openid-connect/auth"
ACCESS_POINT = "https://sso.systemair.com/auth/realms/iot/protocol/openid-connect/token"
GATEWAY_API_URL = "https://homesolutions.systemair.com/gateway/api"
REMOTE_API_URL = "https://homesolutions.systemair.com/gateway/remote-api/"
WEBSOCKET_URL = "wss://homesolutions.systemair.com/streaming"


class UserModes(IntEnum):
    """User modes for ventilation units."""

    AUTO = 0
    MANUAL = 1
    CROWDED = 2
    REFRESH = 3
    FIREPLACE = 4
    AWAY = 5
    HOLIDAY = 6
    COOKER_HOOD = 7
    VACUUM_CLEANER = 8


class APIEndpoints:
    """API endpoints for Systemair API."""

    GATEWAY = GATEWAY_API_URL
    REMOTE = REMOTE_API_URL
    AUTH = AUTH_URL
    TOKEN = ACCESS_POINT

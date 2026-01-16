"""SystemAIR-API - Python library for controlling Systemair ventilation units."""

from .__version__ import __version__
from .api.systemair_api import SystemairAPI
from .api.websocket_client import SystemairWebSocket
from .auth.authenticator import SystemairAuthenticator
from .models.ventilation_unit import VentilationUnit
from .utils.constants import UserModes
from .utils.exceptions import (
    APIError,
    AuthenticationError,
    DeviceNotFoundError,
    RateLimitError,
    SystemairError,
    TokenRefreshError,
    ValidationError,
    WebSocketError,
)

__all__ = [
    "APIError",
    "AuthenticationError",
    "DeviceNotFoundError",
    "RateLimitError",
    "SystemairAPI",
    "SystemairAuthenticator",
    "SystemairError",
    "SystemairWebSocket",
    "TokenRefreshError",
    "UserModes",
    "ValidationError",
    "VentilationUnit",
    "WebSocketError",
    "__version__",
]

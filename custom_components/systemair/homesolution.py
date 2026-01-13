"""Systemair HomeSolution Client."""

import asyncio
import logging
from typing import Any

from .api import SystemairApiClientError, SystemairClientBase
from .homesolution_mapping import PRESET_MODE_TO_VALUE_MAP, PRESET_TO_USER_MODE
from .modbus import parameters_list
from .systemair_api import SystemairAPI, SystemairAuthenticator
from .systemair_api.api.websocket_client import SystemairWebSocket
from .systemair_api.models.ventilation_unit import VentilationUnit
from .systemair_api.utils.exceptions import DeviceOfflineError
from .systemair_api.utils.register_constants import RegisterConstants

_LOGGER = logging.getLogger(__name__)

# Register Constants
REG_USERMODE_MANUAL_AIRFLOW_LEVEL_SAF = 1131
REG_TC_SP = 2001
REG_USERMODE_HMI_CHANGE_REQUEST = 1162
REG_FILTER_REPLACEMENT_TIME_L = 601
REG_ECO_MODE_ON_OFF = 1134


def _build_modbus_to_api_map() -> dict[int, int]:
    """Build a mapping from Modbus register address to API register ID."""
    mapping = {}
    rc_members = RegisterConstants.__members__

    for param in parameters_list:
        # 1. Try exact match
        if param.short in rc_members:
            mapping[param.register] = rc_members[param.short].value
            continue

        # 2. Try REG_MAINBOARD_ prefix
        # If param.short is REG_TC_SP, look for REG_MAINBOARD_TC_SP
        # If param.short is REG_SOMETHING, remove REG_ and add REG_MAINBOARD_
        if param.short.startswith("REG_"):
            suffix = param.short[4:]
            mainboard_name = f"REG_MAINBOARD_{suffix}"
            if mainboard_name in rc_members:
                mapping[param.register] = rc_members[mainboard_name].value
                continue

    return mapping


MODBUS_TO_API = _build_modbus_to_api_map()


class SystemairHomeSolutionClient(SystemairClientBase):
    """Systemair HomeSolution Client."""

    def __init__(self, username: str, password: str, device_id: str) -> None:
        """Initialize."""
        self.username = username
        self.password = password
        self.device_id = device_id
        self.authenticator = SystemairAuthenticator(email=username, password=password)
        self.api = None
        self.websocket = None
        self.unit: VentilationUnit | None = None
        self.update_callback = None
        self._available = False

    async def test_connection(self) -> bool:
        """
        Test connection to the HomeSolution API.

        Attempts to authenticate and verify the device is accessible.
        Returns True if successful, False if connection fails.
        """
        try:
            await asyncio.to_thread(self.authenticator.authenticate)
            api = SystemairAPI(access_token=self.authenticator.access_token)
            await asyncio.to_thread(api.fetch_device_status, self.device_id)

            _LOGGER.info("Successfully connected to HomeSolution API for device %s", self.device_id)
        except Exception:
            _LOGGER.exception("Failed to connect to HomeSolution API")
            return False
        else:
            return True

    async def start(self) -> None:
        """Start the client."""
        await asyncio.to_thread(self.authenticator.authenticate)
        self.api = SystemairAPI(access_token=self.authenticator.access_token)
        self.unit = VentilationUnit(self.device_id, "Systemair Unit")

        # Initial fetch
        try:
            status = await asyncio.to_thread(self.api.fetch_device_status, self.device_id)
            self.unit.update_from_api(status)
            self._available = True
            _LOGGER.info("Device %s is online", self.device_id)
        except DeviceOfflineError as e:
            self._available = False
            _LOGGER.warning("Device %s is offline: %s. Initial data will be empty.", self.device_id, e)
        except Exception as e:  # noqa: BLE001
            self._available = False
            _LOGGER.warning("Failed to fetch initial device status for %s: %s. Initial data will be empty.", self.device_id, e)

        # Setup WebSocket - allow it to fail gracefully
        try:
            self.websocket = SystemairWebSocket(access_token=self.authenticator.access_token, on_message_callback=self._handle_ws_message)
            await asyncio.to_thread(self.websocket.connect)
        except Exception as e:  # noqa: BLE001
            self._available = False
            _LOGGER.warning("Failed to connect WebSocket for device %s: %s. Real-time updates will be unavailable.", self.device_id, e)
            self.websocket = None

    async def stop(self) -> None:
        """Stop the client."""
        if self.websocket is not None:
            try:
                await asyncio.to_thread(self.websocket.disconnect)
            except Exception as e:  # noqa: BLE001
                _LOGGER.warning("Failed to disconnect WebSocket: %s", e)

    async def get_all_data(self, _enable_alarm_history: bool = False) -> VentilationUnit:  # noqa: FBT001, FBT002
        """Get all data."""
        if not self.authenticator.is_token_valid():
            await asyncio.to_thread(self.authenticator.refresh_access_token)
            self.api.update_token(self.authenticator.access_token)

            # Reconnect WS with new token
            if self.websocket is not None:
                try:
                    await asyncio.to_thread(self.websocket.disconnect)
                except Exception as e:  # noqa: BLE001
                    _LOGGER.warning("Failed to disconnect WebSocket during token refresh: %s", e)

            try:
                self.websocket = SystemairWebSocket(
                    access_token=self.authenticator.access_token, on_message_callback=self._handle_ws_message
                )
                await asyncio.to_thread(self.websocket.connect)
            except Exception as e:  # noqa: BLE001
                self._available = False
                _LOGGER.warning("Failed to reconnect WebSocket during token refresh: %s. Real-time updates will be unavailable.", e)
                self.websocket = None

        # We can rely on WebSocket updates, but a periodic poll ensures consistency
        if self.unit is None:
            _LOGGER.warning("Ventilation unit not initialized, returning empty unit")
            self.unit = VentilationUnit(self.device_id, "Systemair Unit")
        return self.unit

    @property
    def available(self) -> bool:
        """Return whether the device is available (online)."""
        return self._available

    async def write_register(self, register: int, value: int) -> bool:
        """Write to a register.

        This translates register writes back to API calls.
        """  # noqa: D213
        # Check if device is available before attempting to write
        if not self._available:
            _LOGGER.warning("Cannot write to offline device %s", self.device_id)
            return False

        # Fan Speed (Manual Mode)
        if register == REG_USERMODE_MANUAL_AIRFLOW_LEVEL_SAF:
            # Value: 0=Off, 2=Low, 3=Normal, 4=High
            # API expects 1-5 (1=Off, 2=Low, 3=Normal, 4=High, 5=Max)
            # Map 0 -> 1
            api_value = 1 if value == 0 else value
            return self.unit.set_value(self.api, "REG_MAINBOARD_USERMODE_MANUAL_AIRFLOW_LEVEL_SAF", api_value, _noprint=True)

        # Temperature Setpoint
        if register == REG_TC_SP:
            return self.unit.set_temperature(self.api, value)

        # Preset Mode (HMI Change Request)
        if register == REG_USERMODE_HMI_CHANGE_REQUEST:
            # Value is 1-based index from climate.py mapping
            preset_mode = next((k for k, v in PRESET_MODE_TO_VALUE_MAP.items() if v == value), None)
            if preset_mode:
                user_mode = PRESET_TO_USER_MODE.get(preset_mode)
                if user_mode is not None:
                    return self.unit.set_user_mode(self.api, user_mode)

        # ECO Mode
        if register == REG_ECO_MODE_ON_OFF:
            return self.unit.set_value(self.api, RegisterConstants.REG_MAINBOARD_ECO_MODE_ON_OFF, value, _noprint=True)

        # Generic mapping
        if register in MODBUS_TO_API:
            api_id = MODBUS_TO_API[register]
            return self.unit.set_value(self.api, api_id, value, _noprint=True)

        _LOGGER.warning("Write to register %s with value %s not implemented for HomeSolution", register, value)
        msg = f"Write to register {register} not supported in HomeSolution"
        raise SystemairApiClientError(msg)

    async def write_registers_32bit(self, address_1based: int, value: int) -> None:
        """Write a 32-bit value across two registers."""
        # Check if device is available before attempting to write
        if not self._available:
            _LOGGER.warning("Cannot write to offline device %s", self.device_id)
            return

        # Filter timer reset (Button)
        if address_1based == REG_FILTER_REPLACEMENT_TIME_L:
            # In HomeSolution, resetting filter is likely a specific command, not a register write.
            # Attempting to write to the mainboard register if mapped
            if address_1based in MODBUS_TO_API:
                api_id = MODBUS_TO_API[address_1based]
                await asyncio.to_thread(self.unit.set_value, self.api, api_id, value, _noprint=True)
                return

            _LOGGER.warning("Resetting filter timer not supported yet for HomeSolution")
            msg = "Resetting filter timer not supported in HomeSolution"
            raise SystemairApiClientError(msg)

        if address_1based in MODBUS_TO_API:
            api_id = MODBUS_TO_API[address_1based]
            await asyncio.to_thread(self.unit.set_value, self.api, api_id, value, _noprint=True)
            return

        _LOGGER.warning("Write to 32-bit register %s with value %s not implemented for HomeSolution", address_1based, value)
        msg = f"Write to 32-bit register {address_1based} not supported in HomeSolution"
        raise SystemairApiClientError(msg)

    def _handle_ws_message(self, message: dict[str, Any]) -> None:
        """Handle incoming WebSocket messages."""
        if message.get("action") == "DEVICE_STATUS_UPDATE":
            # Check if it's for our device
            props = message.get("properties", {})
            if props.get("id") == self.device_id:
                self.unit.update_from_websocket(message)
                if self.update_callback:
                    self.update_callback()
        elif message.get("identifier") == self.device_id:
            self.unit.update_from_websocket(message)
            if self.update_callback:
                self.update_callback()

    def set_update_callback(self, callback: Any) -> None:
        """Set callback for updates."""
        self.update_callback = callback

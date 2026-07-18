"""Systemair HomeSolution Client."""

import asyncio
import logging
from collections.abc import Callable
from time import monotonic
from typing import Any, NoReturn

from .api import SystemairApiClientError, SystemairAuthExpiredError, SystemairClientBase
from .homesolution_mapping import (
    HOMESOLUTION_WRITE_CAPABILITY_ALIASES,
    PARAMETER_BY_REGISTER,
    encode_homesolution_write_value,
    homesolution_write_candidates,
    homesolution_write_capability_id,
)
from .homesolution_views import HomeSolutionViewCatalog
from .modbus import ModbusParameter
from .systemair_api import SystemairAPI, SystemairAuthenticator
from .systemair_api.api.websocket_client import SystemairWebSocket
from .systemair_api.models.ventilation_unit import VentilationUnit
from .systemair_api.utils.exceptions import AuthenticationError, DeviceOfflineError, RateLimitError, SystemairError, TokenRefreshError

_LOGGER = logging.getLogger(__name__)

# Number of consecutive auth failures (refresh + full re-login) tolerated before
# we surface the error to Home Assistant and trigger the reauth flow.
AUTH_FAILURE_THRESHOLD = 20
DEFAULT_RATE_LIMIT_COOLDOWN = 60


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
        self._auth_failure_count = 0
        self._view_catalog = HomeSolutionViewCatalog()
        self._poll_lock = asyncio.Lock()
        self._rate_limit_until = 0.0

    def _merge_refresh_values(self, values: dict[int, Any]) -> None:
        """Replace discovered address metadata and cloud capability values."""
        self.unit.replace_modbus_register_map(getattr(self._view_catalog, "modbus_register_ids", {}))
        self.unit.replace_register_values(values)

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

        # Initial capability discovery and full data fetch
        try:
            result = await asyncio.to_thread(self._view_catalog.discover, self.api, self.device_id)
            if not result.successful_routes:
                self._available = False
                _LOGGER.warning("Device %s did not return any HomeSolution views", self.device_id)
            else:
                self._merge_refresh_values(result.values)
                self._available = True
                _LOGGER.info(
                    "Device %s is online with %d HomeSolution views",
                    self.device_id,
                    len(self._view_catalog.routes),
                )
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
            _LOGGER.warning("Failed to connect WebSocket for device %s: %s. Real-time updates will be unavailable.", self.device_id, e)
            self.websocket = None

    async def stop(self) -> None:
        """Stop the client."""
        if self.websocket is not None:
            try:
                await asyncio.to_thread(self.websocket.disconnect)
            except Exception as e:  # noqa: BLE001
                _LOGGER.warning("Failed to disconnect WebSocket: %s", e)

    async def _ensure_authenticated(self, *, force: bool = False) -> bool:
        """
        Ensure we have a valid access token.

        Returns True if the token was rotated (refresh or full re-login) so callers
        can refresh dependent connections (WebSocket, API client). Falls back to a
        full re-authentication using the stored credentials if the refresh token
        has been invalidated server-side, avoiding a Home Assistant reauth prompt.
        """
        if not force and self.authenticator.is_token_valid():
            return False

        try:
            await asyncio.to_thread(self.authenticator.refresh_access_token)
            _LOGGER.debug("Access token refreshed for device %s", self.device_id)
        except TokenRefreshError as err:
            _LOGGER.info(
                "Refresh token rejected for device %s (%s); performing silent re-authentication",
                self.device_id,
                err,
            )
            await asyncio.to_thread(self.authenticator.authenticate)

        return True

    async def _reconnect_websocket(self) -> None:
        """Disconnect any existing WebSocket and reopen with the current token."""
        if self.websocket is not None:
            try:
                await asyncio.to_thread(self.websocket.disconnect)
            except Exception as e:  # noqa: BLE001
                _LOGGER.warning("Failed to disconnect WebSocket: %s", e)
            self.websocket = None

        try:
            self.websocket = SystemairWebSocket(access_token=self.authenticator.access_token, on_message_callback=self._handle_ws_message)
            await asyncio.to_thread(self.websocket.connect)
        except Exception as e:  # noqa: BLE001
            _LOGGER.warning("Failed to reconnect WebSocket: %s. Real-time updates will be unavailable.", e)
            self.websocket = None

    async def _prepare_api_request(self, *, force: bool = False) -> None:
        """Refresh the HTTP token and dependent WebSocket when necessary."""
        if await self._ensure_authenticated(force=force):
            self.api.update_token(self.authenticator.access_token)
            await self._reconnect_websocket()

    async def _execute_api_request(self, operation: Callable[[], Any]) -> Any:
        """Execute one cloud request, rotating a server-rejected token once."""
        remaining_cooldown = self._rate_limit_until - monotonic()
        if remaining_cooldown > 0:
            raise RateLimitError(retry_after=max(1, int(remaining_cooldown)))
        await self._prepare_api_request()
        try:
            try:
                result = await asyncio.to_thread(operation)
            except AuthenticationError:
                await self._prepare_api_request(force=True)
                result = await asyncio.to_thread(operation)
        except RateLimitError as err:
            retry_after = err.retry_after or DEFAULT_RATE_LIMIT_COOLDOWN
            self._rate_limit_until = max(self._rate_limit_until, monotonic() + retry_after)
            raise
        self._auth_failure_count = 0
        self._rate_limit_until = 0.0
        return result

    def _raise_authentication_failure(self, err: AuthenticationError) -> NoReturn:
        """Count a failed token recovery and eventually request Home Assistant reauth."""
        self._available = False
        self._auth_failure_count += 1
        if self._auth_failure_count >= AUTH_FAILURE_THRESHOLD:
            _LOGGER.exception(
                "Authentication failed %d times in a row for device %s; surfacing reauth",
                self._auth_failure_count,
                self.device_id,
            )
            msg = f"Authentication failed {self._auth_failure_count} times: {err}"
            raise SystemairAuthExpiredError(msg) from err

        _LOGGER.warning(
            "Authentication failed for device %s (attempt %d/%d): %s",
            self.device_id,
            self._auth_failure_count,
            AUTH_FAILURE_THRESHOLD,
            err,
        )
        msg = f"Authentication failed (attempt {self._auth_failure_count}/{AUTH_FAILURE_THRESHOLD}): {err}"
        raise SystemairApiClientError(msg) from err

    async def get_all_data(
        self,
        *,
        _enable_alarm_details: bool = True,
        _enable_alarm_history: bool = False,
    ) -> VentilationUnit:
        """Get all data."""
        if self._rate_limit_until > monotonic() and self.unit is not None and self.unit.registers:
            return self.unit

        try:
            await self._prepare_api_request()
            if self.websocket is None:
                # Token still valid but WS was lost (e.g. transient network drop).
                # Re-open it so real-time updates resume without waiting for a token rotation.
                await self._reconnect_websocket()
        except AuthenticationError as err:
            self._raise_authentication_failure(err)

        # We can rely on WebSocket updates, but a periodic poll ensures consistency
        if self.unit is None:
            _LOGGER.warning("Ventilation unit not initialized, returning empty unit")
            self.unit = VentilationUnit(self.device_id, "Systemair Unit")

        try:
            async with self._poll_lock:
                result = await self._execute_api_request(lambda: self._view_catalog.refresh(self.api, self.device_id))
                if result.successful_routes:
                    self._merge_refresh_values(result.values)
                    self._available = True
                else:
                    self._available = False
                    msg = "Failed to refresh any HomeSolution views"
                    raise SystemairApiClientError(msg)
                if result.errors:
                    _LOGGER.warning(
                        "HomeSolution refresh completed with %d unavailable views for device %s",
                        len(result.errors),
                        self.device_id,
                    )
        except RateLimitError as err:
            if self.unit.registers:
                _LOGGER.warning(
                    "HomeSolution rate limit reached for device %s; serving the cached snapshot for %d seconds",
                    self.device_id,
                    err.retry_after or DEFAULT_RATE_LIMIT_COOLDOWN,
                )
                return self.unit
            self._available = False
            msg = f"HomeSolution refresh rate limited: {err}"
            raise SystemairApiClientError(msg) from err
        except AuthenticationError as err:
            self._raise_authentication_failure(err)
        except SystemairError as err:
            self._available = False
            msg = f"HomeSolution refresh failed: {err}"
            raise SystemairApiClientError(msg) from err
        return self.unit

    @property
    def available(self) -> bool:
        """Return whether the device is available (online)."""
        return self._available

    def can_write_register(self, register: ModbusParameter) -> bool:
        """Return whether discovery exposed a writable control for a SAVE register."""
        return self.unit is not None and self._write_target(register) is not None

    def can_write_registers_32bit(self, register: ModbusParameter) -> bool:
        """Return whether both halves of a split value are writable capabilities."""
        high_parameter = PARAMETER_BY_REGISTER.get(register.combine_with_32_bit) if register.combine_with_32_bit is not None else None
        return high_parameter is not None and self.can_write_register(register) and self.can_write_register(high_parameter)

    def _write_target(self, register: ModbusParameter) -> tuple[int, int] | None:
        """Return the action ID and visible capability proving it is supported."""
        candidates = list(homesolution_write_candidates(register))
        mapped_register_id = self.unit.modbus_register_ids.get(register.register - 1) if self.unit is not None else None
        if mapped_register_id is not None and mapped_register_id not in candidates:
            if register.short in HOMESOLUTION_WRITE_CAPABILITY_ALIASES:
                candidates.append(mapped_register_id)
            else:
                candidates.insert(0, mapped_register_id)
        for register_id in candidates:
            capability_id = homesolution_write_capability_id(register, register_id)
            if self._view_catalog.is_register_writable(capability_id) or self._view_catalog.is_register_writable(register_id):
                return register_id, capability_id
        return None

    async def _refresh_after_write(self, register_ids: tuple[int, ...]) -> None:
        """Refresh and merge the views containing changed data items."""
        routes = tuple(
            dict.fromkeys(route for register_id in register_ids for route in self._view_catalog.routes_for_register(register_id))
        )
        if not routes:
            return

        try:
            async with self._poll_lock:
                result = await self._execute_api_request(lambda: self._view_catalog.refresh_routes(self.api, self.device_id, routes))
                if result.successful_routes:
                    self._merge_refresh_values(result.values)
                    self._available = True
                if result.errors:
                    _LOGGER.warning(
                        "HomeSolution post-write refresh had %d unavailable views for device %s",
                        len(result.errors),
                        self.device_id,
                    )
        except SystemairError as err:
            _LOGGER.warning(
                "HomeSolution accepted a write for device %s but its immediate readback failed: %s",
                self.device_id,
                err,
            )

    async def write_register(self, register: int, value: int) -> bool:
        """Write through the writable HomeSolution capability for a SAVE register."""
        if not self._available:
            msg = f"Cannot write to offline HomeSolution device {self.device_id}"
            raise SystemairApiClientError(msg)
        parameter = PARAMETER_BY_REGISTER.get(register)
        if parameter is None or (write_target := self._write_target(parameter)) is None:
            msg = f"Register {register} is not exposed as a writable HomeSolution capability"
            raise SystemairApiClientError(msg)

        target, capability = write_target
        encoded_value = encode_homesolution_write_value(parameter, value)
        try:
            success = await self._execute_api_request(lambda: self.unit.set_value(self.api, target, encoded_value, _noprint=True))
            if not success:
                msg = f"HomeSolution rejected write to register {register}"
                raise SystemairApiClientError(msg)
            await self._refresh_after_write((capability,))
        except AuthenticationError as err:
            self._raise_authentication_failure(err)
        except SystemairError as err:
            msg = f"HomeSolution write to register {register} failed: {err}"
            raise SystemairApiClientError(msg) from err
        return True

    async def write_registers_32bit(self, address_1based: int, value: int) -> None:
        """Write a split 32-bit value when both cloud capabilities are writable."""
        if not self._available:
            msg = f"Cannot write to offline HomeSolution device {self.device_id}"
            raise SystemairApiClientError(msg)

        low_parameter = PARAMETER_BY_REGISTER.get(address_1based)
        high_parameter = (
            PARAMETER_BY_REGISTER.get(low_parameter.combine_with_32_bit)
            if low_parameter is not None and low_parameter.combine_with_32_bit is not None
            else None
        )
        low_write_target = self._write_target(low_parameter) if low_parameter is not None else None
        high_write_target = self._write_target(high_parameter) if high_parameter is not None else None
        if low_write_target is None or high_write_target is None:
            msg = f"32-bit register {address_1based} is not exposed as writable HomeSolution capabilities"
            raise SystemairApiClientError(msg)
        low_target, low_capability = low_write_target
        high_target, high_capability = high_write_target

        try:
            result = await self._execute_api_request(
                lambda: self.api.write_data_items(
                    self.device_id,
                    (
                        (low_target, value & 0xFFFF),
                        (high_target, (value >> 16) & 0xFFFF),
                    ),
                )
            )
            if not result.get("data", {}).get("WriteDataItems"):
                msg = f"HomeSolution rejected 32-bit write to register {address_1based}"
                raise SystemairApiClientError(msg)
            await self._refresh_after_write((low_capability, high_capability))
        except AuthenticationError as err:
            self._raise_authentication_failure(err)
        except SystemairError as err:
            msg = f"HomeSolution 32-bit write to register {address_1based} failed: {err}"
            raise SystemairApiClientError(msg) from err

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

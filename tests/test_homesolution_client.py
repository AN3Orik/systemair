"""Business tests for HomeSolution polling and availability."""

# ruff: noqa: PLR2004, S101, S105, SLF001

from __future__ import annotations

import asyncio
import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, patch

from custom_components.systemair.coordinator import SystemairDataUpdateCoordinator
from custom_components.systemair.homesolution import SystemairHomeSolutionClient
from custom_components.systemair.homesolution_views import HomeSolutionRefreshResult
from custom_components.systemair.modbus import parameter_map
from custom_components.systemair.systemair_api.models.ventilation_unit import VentilationUnit
from custom_components.systemair.systemair_api.utils.exceptions import APIError
from custom_components.systemair.systemair_api.utils.register_constants import RegisterConstants


class FakeAuthenticator:
    """Keep the polling test on the already-authenticated path."""

    access_token = "token"

    @staticmethod
    def is_token_valid() -> bool:
        """Return an active token."""
        return True

    @staticmethod
    def authenticate() -> str:
        """Return a token without network access."""
        return "token"


class FakeCatalog:
    """Return one successful route and one partial error."""

    routes = ("/home",)

    def __init__(self) -> None:
        """Track refresh calls."""
        self.calls = 0
        self.route_refreshes: list[tuple[str, ...]] = []

    def refresh(self, _api: object, _device_id: str) -> HomeSolutionRefreshResult:
        """Return a complete refresh result."""
        self.calls += 1
        return HomeSolutionRefreshResult(
            values={29: 3, 31: 4},
            errors={"/service/unavailable": "Unsupported view"},
            successful_routes=frozenset({"/home"}),
        )

    def discover(self, _api: object, _device_id: str) -> HomeSolutionRefreshResult:
        """Return an initial capability snapshot."""
        self.calls += 1
        return HomeSolutionRefreshResult(values={29: 3}, errors={}, successful_routes=frozenset({"/home"}))

    @staticmethod
    def is_register_writable(register_id: int) -> bool:
        """Expose the writable controls present on the fake home view."""
        return register_id in {
            RegisterConstants.REG_MAINBOARD_USERMODE_MODE_HMI,
            RegisterConstants.REG_MAINBOARD_SPEED_INDICATION_APP,
            RegisterConstants.REG_MAINBOARD_TC_SP,
            900,
        }

    @staticmethod
    def route_for_register(register_id: int) -> str | None:
        """Place fake writable controls on the home view."""
        if register_id == 900:
            return "/service/settings"
        return "/home" if FakeCatalog.is_register_writable(register_id) else None

    def refresh_routes(self, _api: object, _device_id: str, routes: tuple[str, ...]) -> HomeSolutionRefreshResult:
        """Return the route refreshed immediately after a command."""
        self.route_refreshes.append(routes)
        return HomeSolutionRefreshResult(values={29: 3, 31: 2}, errors={}, successful_routes=frozenset(routes))


class FailingPostWriteCatalog(FakeCatalog):
    """Accept discovery but fail the optional command readback."""

    def refresh_routes(self, _api: object, _device_id: str, _routes: tuple[str, ...]) -> HomeSolutionRefreshResult:
        """Simulate a temporary device timeout after an accepted mutation."""
        msg = "Device request timed out"
        raise APIError(msg)


class HomeSolutionClientTest(unittest.TestCase):
    """The cloud client polls all views independently of WebSocket state."""

    def test_get_all_data_refreshes_catalog_and_restores_availability(self) -> None:
        """A partial view error preserves successful data and online state."""
        client = SystemairHomeSolutionClient("user", "password", "device")
        client.authenticator = FakeAuthenticator()
        client.api = object()
        client.websocket = object()
        client.unit = VentilationUnit("device", "Unit")
        client._view_catalog = FakeCatalog()
        client._available = False

        with self.assertLogs("custom_components.systemair.homesolution", level="WARNING"):
            unit = asyncio.run(client.get_all_data())

        assert client._view_catalog.calls == 1
        assert unit.registers[29] == 3
        assert unit.registers[31] == 4
        assert client.available is True

    def test_start_discovers_views_before_websocket(self) -> None:
        """Initial startup populates capabilities without relying on WebSocket."""
        client = SystemairHomeSolutionClient("user", "password", "device")
        client.authenticator = FakeAuthenticator()
        client._view_catalog = FakeCatalog()
        fake_api = Mock()
        fake_api.fetch_device_status.return_value = {"data": {"GetView": {"children": []}}}
        fake_websocket = Mock()

        with (
            patch("custom_components.systemair.homesolution.SystemairAPI", return_value=fake_api),
            patch("custom_components.systemair.homesolution.SystemairWebSocket", return_value=fake_websocket),
        ):
            asyncio.run(client.start())

        assert client._view_catalog.calls == 1
        assert client.unit.registers[29] == 3
        assert client.available is True

    def test_websocket_failure_does_not_override_successful_http_poll(self) -> None:
        """Optional real-time transport cannot mark a polled device offline."""
        client = SystemairHomeSolutionClient("user", "password", "device")
        client.authenticator = FakeAuthenticator()
        client._view_catalog = FakeCatalog()
        fake_websocket = Mock()
        fake_websocket.connect.side_effect = OSError("websocket unavailable")

        with (
            patch("custom_components.systemair.homesolution.SystemairAPI", return_value=Mock()),
            patch("custom_components.systemair.homesolution.SystemairWebSocket", return_value=fake_websocket),
            self.assertLogs("custom_components.systemair.homesolution", level="WARNING"),
        ):
            asyncio.run(client.start())

        assert client.available is True
        assert client.websocket is None

    def test_write_uses_discovered_control_and_refreshes_its_route(self) -> None:
        """Commands target writable capabilities and immediately merge the changed view."""
        client = SystemairHomeSolutionClient("user", "password", "device")
        client.authenticator = FakeAuthenticator()
        client.api = Mock()
        client.api.write_data_item.return_value = {"data": {"WriteDataItems": True}}
        client.unit = VentilationUnit("device", "Unit")
        client._view_catalog = FakeCatalog()
        client._available = True

        result = asyncio.run(client.write_register(parameter_map["REG_USERMODE_HMI_CHANGE_REQUEST"].register, 4))

        assert result is True
        client.api.write_data_item.assert_called_once_with(
            "device",
            RegisterConstants.REG_MAINBOARD_USERMODE_HMI_CHANGE_REQUEST,
            4,
        )
        assert client._view_catalog.route_refreshes == [("/home",)]
        assert client.can_write_register(parameter_map["REG_USERMODE_HMI_CHANGE_REQUEST"]) is True

    def test_post_write_readback_failure_does_not_reject_accepted_command(self) -> None:
        """A temporary readback timeout is deferred to the next coordinator poll."""
        client = SystemairHomeSolutionClient("user", "password", "device")
        client.authenticator = FakeAuthenticator()
        client.api = Mock()
        client.api.write_data_item.return_value = {"data": {"WriteDataItems": True}}
        client.unit = VentilationUnit("device", "Unit")
        client._view_catalog = FailingPostWriteCatalog()
        client._available = True

        with self.assertLogs("custom_components.systemair.homesolution", level="WARNING"):
            result = asyncio.run(client.write_register(parameter_map["REG_TC_SP"].register, 220))

        assert result is True

    def test_generic_write_uses_discovered_modbus_metadata_target(self) -> None:
        """Writable service settings do not require a hand-maintained cloud alias."""
        client = SystemairHomeSolutionClient("user", "password", "device")
        client.authenticator = FakeAuthenticator()
        client.api = Mock()
        client.api.write_data_item.return_value = {"data": {"WriteDataItems": True}}
        client.unit = VentilationUnit("device", "Unit")
        register = parameter_map["REG_DEMC_RH_SETTINGS_SP_WINTER"]
        client.unit.update_modbus_register_map({register.register - 1: 900})
        client.unit.registers[900] = 45
        client._view_catalog = FakeCatalog()
        client._available = True

        result = asyncio.run(client.write_register(register.register, 50))

        assert result is True
        client.api.write_data_item.assert_called_once_with("device", 900, 50)
        assert client._view_catalog.route_refreshes == [("/service/settings",)]

    def test_cloud_post_write_refresh_publishes_cache_without_full_poll(self) -> None:
        """Repeated platform refresh hooks cannot fan out into full cloud crawls."""
        coordinator = SystemairDataUpdateCoordinator.__new__(SystemairDataUpdateCoordinator)
        unit = object()
        coordinator._is_homesolution = True
        coordinator.client = SimpleNamespace(unit=unit)
        coordinator.async_set_updated_data = Mock()
        coordinator.async_request_refresh = AsyncMock()

        asyncio.run(coordinator.async_refresh_after_write())

        coordinator.async_set_updated_data.assert_called_once_with(unit)
        coordinator.async_request_refresh.assert_not_awaited()


if __name__ == "__main__":
    unittest.main()

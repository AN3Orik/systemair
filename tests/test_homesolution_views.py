"""Business tests for HomeSolution view ingestion."""

# ruff: noqa: PLR2004, S101

from __future__ import annotations

import importlib
import importlib.util
import unittest
from unittest.mock import Mock, patch

import requests

from custom_components.systemair.systemair_api.api.systemair_api import HomeSolutionViewsResponse, SystemairAPI
from custom_components.systemair.systemair_api.models.ventilation_unit import VentilationUnit
from custom_components.systemair.systemair_api.utils.exceptions import APIError, AuthenticationError
from custom_components.systemair.systemair_api.utils.register_constants import RegisterConstants


class HomeSolutionViewsTest(unittest.TestCase):
    """HomeSolution views preserve partial results and nested data items."""

    def test_nested_data_items_are_ingested(self) -> None:
        """Registers nested in rows and tabs are stored in the unit cache."""
        unit = VentilationUnit("device", "Unit")
        unit.update_from_api(
            {
                "data": {
                    "GetView": {
                        "children": [
                            {
                                "properties": {
                                    "rows": [
                                        {"dataItem": {"id": 101, "value": 11}},
                                        {"tabs": [{"dataItem": {"id": 202, "value": 22}}]},
                                    ]
                                }
                            }
                        ]
                    }
                }
            }
        )

        assert unit.registers == {101: 11, 202: 22}

    def test_active_function_registers_update_named_flags(self) -> None:
        """Active-function data items use complete enum names without crashing."""
        unit = VentilationUnit("device", "Unit")
        try:
            unit.update_register_values(
                {
                    RegisterConstants.REG_MAINBOARD_FUNCTION_ACTIVE_COOLING: 1,
                    RegisterConstants.REG_MAINBOARD_FUNCTION_ACTIVE_HEAT_RECOVERY: 1,
                }
            )
        except AttributeError as err:
            self.fail(f"Active function parsing raised {err!r}")

        assert unit.active_functions["cooling"] == 1
        assert unit.active_functions["heat_recovery"] == 1

    def test_numeric_string_values_are_decoded_for_summary_fields(self) -> None:
        """GraphQL numeric strings can populate typed unit summary fields."""
        unit = VentilationUnit("device", "Unit")

        unit.update_register_values({RegisterConstants.REG_MAINBOARD_TC_SP: "215"})

        assert unit.registers[RegisterConstants.REG_MAINBOARD_TC_SP] == 215
        assert unit.temperatures["setpoint"] == 21.5

    def test_removed_temperature_capabilities_clear_summary_fields(self) -> None:
        """A removed cloud capability cannot leave its previous temperature visible."""
        unit = VentilationUnit("device", "Unit")
        unit.update_register_values(
            {
                RegisterConstants.REG_MAINBOARD_TC_SP: 215,
                RegisterConstants.REG_MAINBOARD_SENSOR_OAT: 50,
            }
        )

        unit.replace_register_values({})

        assert unit.registers == {}
        assert unit.temperatures["setpoint"] is None
        assert unit.temperatures["oat"] is None

    def test_text_capability_value_is_preserved_without_numeric_conversion(self) -> None:
        """Unmapped textual capabilities do not trigger eager temperature math."""
        unit = VentilationUnit("device", "Unit")

        unit.update_register_values({99999: "status text"})

        assert unit.registers[99999] == "status text"

    def test_batched_get_view_preserves_partial_success(self) -> None:
        """A GraphQL error for one alias does not discard another view."""
        api = SystemairAPI.__new__(SystemairAPI)
        api.headers = {"Authorization": "Bearer redacted"}
        response = Mock()
        response.status_code = 200
        response.json.return_value = {
            "data": {
                "v0": {"children": [{"type": "value", "properties": {}}]},
                "v1": None,
            },
            "errors": [{"message": "Unsupported view", "path": ["v1"]}],
        }
        response.raise_for_status.return_value = None

        method = getattr(api, "fetch_device_views", None)
        assert method is not None
        with patch("custom_components.systemair.systemair_api.api.systemair_api.requests.post", return_value=response) as post:
            result = method("device", ("/home", "/settings"))

        assert result.views["/home"] is not None
        assert result.views["/settings"] is None
        assert result.errors == {"/settings": "Unsupported view"}
        payload = post.call_args.kwargs["json"]
        assert payload["variables"] == {
            "i0": {"route": "/home", "viewId": ""},
            "i1": {"route": "/settings", "viewId": ""},
        }
        assert "v0: GetView" in payload["query"]
        assert "v1: GetView" in payload["query"]

    def test_batched_get_view_rejects_unassociated_graphql_errors(self) -> None:
        """A request-level GraphQL failure cannot masquerade as a clean partial response."""
        api = SystemairAPI.__new__(SystemairAPI)
        api.headers = {"Authorization": "Bearer redacted"}
        response = Mock()
        response.status_code = 200
        response.json.return_value = {
            "data": {"v0": {"children": []}},
            "errors": [{"message": "Gateway failed", "path": []}],
        }
        response.raise_for_status.return_value = None

        with (
            patch("custom_components.systemair.systemair_api.api.systemair_api.requests.post", return_value=response),
            self.assertRaises(APIError),  # noqa: PT027 -- suite intentionally uses unittest
        ):
            api.fetch_device_views("device", ("/home",))

    def test_batched_get_view_wraps_http_failures_as_api_errors(self) -> None:
        """Transport failures stay inside the bundled API exception hierarchy."""
        api = SystemairAPI.__new__(SystemairAPI)
        api.headers = {"Authorization": "Bearer redacted"}
        response = Mock()
        response.status_code = 500
        response.raise_for_status.side_effect = requests.HTTPError("server busy", response=response)

        with (
            patch("custom_components.systemair.systemair_api.api.systemair_api.requests.post", return_value=response),
            self.assertRaises(APIError),  # noqa: PT027 -- suite intentionally uses unittest
        ):
            api.fetch_device_views("device", ("/home",))

    def test_batched_get_view_reports_expired_http_authentication(self) -> None:
        """An invalid cloud token remains distinguishable from a transport failure."""
        api = SystemairAPI.__new__(SystemairAPI)
        api.headers = {"Authorization": "Bearer redacted"}
        response = Mock()
        response.status_code = 401
        response.json.return_value = {"message": "Unauthorized"}
        response.raise_for_status.side_effect = requests.HTTPError("unauthorized", response=response)

        with (
            patch("custom_components.systemair.systemair_api.api.systemair_api.requests.post", return_value=response),
            self.assertRaises(AuthenticationError),  # noqa: PT027 -- suite intentionally uses unittest
        ):
            api.fetch_device_views("device", ("/home",))

    def test_write_data_items_sends_one_atomic_mutation(self) -> None:
        """A split SAVE value is written as one HomeSolution mutation."""
        api = SystemairAPI.__new__(SystemairAPI)
        api.headers = {"Authorization": "Bearer redacted"}
        response = Mock()
        response.status_code = 200
        response.json.return_value = {"data": {"WriteDataItems": True}}
        response.raise_for_status.return_value = None

        with patch("custom_components.systemair.systemair_api.api.systemair_api.requests.post", return_value=response) as post:
            result = api.write_data_items("device", ((101, 0x1234), (102, 0x5678)))

        assert result["data"]["WriteDataItems"] is True
        assert post.call_args.kwargs["json"]["variables"] == {
            "input": {
                "dataPoints": [
                    {"id": 101, "value": str(0x1234)},
                    {"id": 102, "value": str(0x5678)},
                ]
            }
        }

    def test_catalog_discovers_and_refreshes_all_linked_views(self) -> None:
        """Relative view links become a stable catalog refreshed in full."""
        module_name = "custom_components.systemair.homesolution_views"
        assert importlib.util.find_spec(module_name) is not None
        views_module = importlib.import_module(module_name)

        class FakeAPI:
            def __init__(self) -> None:
                self.calls: list[tuple[str, ...]] = []

            def fetch_device_views(self, _device_id: str, routes: tuple[str, ...]) -> HomeSolutionViewsResponse:
                self.calls.append(routes)
                views = {
                    "/home": {
                        "children": [
                            {
                                "properties": {
                                    "enabled": True,
                                    "dataItem": {
                                        "id": 1,
                                        "value": 10,
                                        "readOnly": False,
                                        "extension": {"modbusRegister": 2000},
                                    },
                                }
                            },
                            {
                                "properties": {
                                    "enabled": False,
                                    "dataItem": {
                                        "id": 3,
                                        "value": 30,
                                        "readOnly": False,
                                        "extension": {"modbusRegister": 2002},
                                    },
                                }
                            },
                            {"properties": {"route": "service"}},
                        ]
                    },
                    "/service": {"children": [{"properties": {"route": "service/output"}}]},
                    "/service/output": {
                        "children": [{"properties": {"rows": [{"enabled": True, "dataItem": {"id": 2, "value": 20, "readOnly": True}}]}}]
                    },
                }
                return HomeSolutionViewsResponse(views={route: views.get(route) for route in routes}, errors={})

        api = FakeAPI()
        catalog = views_module.HomeSolutionViewCatalog(seed_routes=("/home",), batch_size=2, max_routes=10)

        discovered = catalog.discover(api, "device")

        assert discovered.values == {1: 10, 2: 20}
        assert catalog.routes == ("/home", "/service", "/service/output")
        assert catalog.route_for_register(1) == "/home"
        assert catalog.route_for_register(2) == "/service/output"
        assert catalog.register_id_for_modbus(2001) == 1
        assert catalog.register_id_for_modbus(2003) is None
        assert catalog.is_register_writable(1) is True
        assert catalog.is_register_writable(2) is False
        assert catalog.is_register_writable(3) is False

        api.calls.clear()
        refreshed = catalog.refresh(api, "device")
        assert refreshed.values == {1: 10, 2: 20}
        assert api.calls == [("/home", "/service"), ("/service/output",)]

        api.calls.clear()
        refreshed = catalog.refresh_routes(api, "device", ("/service/output",))
        assert refreshed.values == {1: 10, 2: 20}
        assert api.calls == [("/service/output",)]

    def test_default_catalog_discovers_every_device_capability_root(self) -> None:
        """Independent SAVE view trees participate in the same 60-second snapshot."""
        expected_routes = (
            "/home",
            "/home/active_functions_home",
            "/home/changeMode",
            "/home/change_airflow",
            "/home/change_temperature",
            "/service",
            "/alarms",
            "/unit_information",
            "/unit_monitoring",
            "/week_schedule",
            "/week_schedule/edit",
            "/week_schedule/settings",
        )

        class FakeAPI:
            @staticmethod
            def fetch_device_views(_device_id: str, routes: tuple[str, ...]) -> HomeSolutionViewsResponse:
                views = {
                    route: {
                        "children": [
                            {
                                "properties": {
                                    "enabled": True,
                                    "dataItem": {"id": index, "value": index, "readOnly": True},
                                }
                            }
                        ]
                    }
                    for index, route in enumerate(expected_routes, start=1)
                }
                return HomeSolutionViewsResponse(views={route: views.get(route) for route in routes}, errors={})

        catalog = importlib.import_module("custom_components.systemair.homesolution_views").HomeSolutionViewCatalog()

        result = catalog.discover(FakeAPI(), "device")

        assert catalog.routes == expected_routes
        assert result.values == {index: index for index in range(1, len(expected_routes) + 1)}

    def test_successful_route_refresh_replaces_removed_capabilities(self) -> None:
        """Conditional controls stop being readable or writable as soon as their view disables them."""

        class FakeAPI:
            enabled = True

            def fetch_device_views(self, _device_id: str, routes: tuple[str, ...]) -> HomeSolutionViewsResponse:
                children = [
                    {
                        "properties": {
                            "enabled": self.enabled,
                            "dataItem": {
                                "id": 1,
                                "value": 10,
                                "readOnly": False,
                                "extension": {"modbusRegister": 2000},
                            },
                        }
                    }
                ]
                if not self.enabled:
                    children.append(
                        {
                            "properties": {
                                "enabled": True,
                                "dataItem": {
                                    "id": 2,
                                    "value": 20,
                                    "readOnly": True,
                                    "extension": {"modbusRegister": 2001},
                                },
                            }
                        }
                    )
                return HomeSolutionViewsResponse(views={route: {"children": children} for route in routes}, errors={})

        api = FakeAPI()
        catalog = importlib.import_module("custom_components.systemair.homesolution_views").HomeSolutionViewCatalog(seed_routes=("/home",))
        catalog.discover(api, "device")
        api.enabled = False

        refreshed = catalog.refresh(api, "device")

        assert refreshed.values == {2: 20}
        assert catalog.route_for_register(1) is None
        assert catalog.is_register_writable(1) is False
        assert catalog.register_id_for_modbus(2001) is None
        assert catalog.register_id_for_modbus(2002) == 2

    def test_catalog_skips_the_unit_software_update_action_view(self) -> None:
        """The frontend-only update flow cannot break normal capability polling."""

        class FakeAPI:
            def __init__(self) -> None:
                self.calls: list[tuple[str, ...]] = []

            def fetch_device_views(self, _device_id: str, routes: tuple[str, ...]) -> HomeSolutionViewsResponse:
                self.calls.append(routes)
                return HomeSolutionViewsResponse(
                    views={
                        route: {
                            "children": [{"properties": {"route": "unit_information/versions/update"}}]
                            if route == "/unit_information"
                            else []
                        }
                        for route in routes
                    },
                    errors={},
                )

        api = FakeAPI()
        catalog = importlib.import_module("custom_components.systemair.homesolution_views").HomeSolutionViewCatalog(
            seed_routes=("/unit_information",)
        )

        catalog.discover(api, "device")

        assert catalog.routes == ("/unit_information",)
        assert api.calls == [("/unit_information",)]

    def test_catalog_tracks_every_route_owning_a_duplicate_register(self) -> None:
        """Post-write readback can refresh every snapshot containing one data item."""

        class FakeAPI:
            @staticmethod
            def fetch_device_views(_device_id: str, routes: tuple[str, ...]) -> HomeSolutionViewsResponse:
                return HomeSolutionViewsResponse(
                    views={
                        route: {
                            "children": [
                                {
                                    "properties": {
                                        "enabled": True,
                                        "dataItem": {"id": 1, "value": 10, "readOnly": False},
                                    }
                                }
                            ]
                        }
                        for route in routes
                    },
                    errors={},
                )

        catalog = importlib.import_module("custom_components.systemair.homesolution_views").HomeSolutionViewCatalog(
            seed_routes=("/home", "/home/changeMode")
        )

        catalog.discover(FakeAPI(), "device")

        assert catalog.routes_for_register(1) == ("/home", "/home/changeMode")

    def test_fresh_duplicate_value_wins_when_another_owner_fails_to_refresh(self) -> None:
        """A failed duplicate route cannot overwrite a value refreshed by another owner."""

        class FakeAPI:
            fail_change_mode = False

            def fetch_device_views(self, _device_id: str, routes: tuple[str, ...]) -> HomeSolutionViewsResponse:
                views = {
                    route: {
                        "children": [
                            {
                                "properties": {
                                    "enabled": True,
                                    "dataItem": {"id": 1, "value": 4 if self.fail_change_mode and route == "/home" else 1},
                                }
                            }
                        ]
                    }
                    for route in routes
                }
                errors = {}
                if self.fail_change_mode and "/home/changeMode" in routes:
                    views["/home/changeMode"] = None
                    errors["/home/changeMode"] = "temporary failure"
                return HomeSolutionViewsResponse(views=views, errors=errors)

        api = FakeAPI()
        catalog = importlib.import_module("custom_components.systemair.homesolution_views").HomeSolutionViewCatalog(
            seed_routes=("/home", "/home/changeMode")
        )
        catalog.discover(api, "device")
        api.fail_change_mode = True

        refreshed = catalog.refresh_routes(api, "device", ("/home", "/home/changeMode"))

        assert refreshed.values[1] == 4


if __name__ == "__main__":
    unittest.main()

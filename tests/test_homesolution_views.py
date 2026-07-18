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
from custom_components.systemair.systemair_api.utils.exceptions import APIError
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
                                    "dataItem": {
                                        "id": 1,
                                        "value": 10,
                                        "readOnly": False,
                                        "extension": {"modbusRegister": 2000},
                                    }
                                }
                            },
                            {"properties": {"route": "service"}},
                        ]
                    },
                    "/service": {"children": [{"properties": {"route": "service/output"}}]},
                    "/service/output": {"children": [{"properties": {"rows": [{"dataItem": {"id": 2, "value": 20, "readOnly": True}}]}}]},
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
        assert catalog.is_register_writable(1) is True
        assert catalog.is_register_writable(2) is False

        api.calls.clear()
        refreshed = catalog.refresh(api, "device")
        assert refreshed.values == {1: 10, 2: 20}
        assert api.calls == [("/home", "/service"), ("/service/output",)]

        api.calls.clear()
        refreshed = catalog.refresh_routes(api, "device", ("/service/output",))
        assert refreshed.values == {2: 20}
        assert api.calls == [("/service/output",)]


if __name__ == "__main__":
    unittest.main()

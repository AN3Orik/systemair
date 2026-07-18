"""Capability discovery for Systemair HomeSolution views."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Protocol

if TYPE_CHECKING:
    from collections.abc import Iterable

CAPABILITY_VIEW_ROOTS = ("/home", "/service", "/alarms", "/unit_information", "/unit_monitoring", "/week_schedule")
DEFAULT_VIEW_ROUTES = (
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
NON_CAPABILITY_VIEW_ROUTES = frozenset({"/unit_information/versions/update"})
DEFAULT_VIEW_BATCH_SIZE = 10
DEFAULT_MAX_VIEW_ROUTES = 220


class HomeSolutionViewsAPI(Protocol):
    """Protocol implemented by the synchronous HomeSolution API client."""

    def fetch_device_views(self, device_id: str, routes: tuple[str, ...]) -> Any:
        """Fetch a batch of views."""


@dataclass(frozen=True)
class HomeSolutionRefreshResult:
    """Values and per-route errors returned by one catalog operation."""

    values: dict[int, Any]
    errors: dict[str, str]
    successful_routes: frozenset[str]


@dataclass(frozen=True)
class _HomeSolutionViewCapabilities:
    """Capability snapshot returned by one successful view request."""

    values: dict[int, Any]
    routes: set[str]
    register_ids: set[int]
    writable_registers: set[int]
    modbus_register_ids: dict[int, int]


def normalize_view_route(route: Any) -> str | None:
    """Normalize a linked HomeSolution route and reject unrelated navigation."""
    if not isinstance(route, str) or not route.strip():
        return None
    normalized = route.strip()
    if not normalized.startswith("/"):
        normalized = f"/{normalized}"
    if normalized in NON_CAPABILITY_VIEW_ROUTES:
        return None
    return normalized if any(normalized == root or normalized.startswith(f"{root}/") for root in CAPABILITY_VIEW_ROOTS) else None


def extract_view_data(view: Any) -> tuple[dict[int, Any], set[str]]:
    """Extract register values and linked routes from an arbitrarily nested view."""
    capabilities = _extract_view_capabilities(view)
    return capabilities.values, capabilities.routes


def _extract_view_capabilities(view: Any) -> _HomeSolutionViewCapabilities:
    """Extract values, links, and writable data-item capabilities from a view."""
    values: dict[int, Any] = {}
    routes: set[str] = set()
    register_ids: set[int] = set()
    writable_registers: set[int] = set()
    modbus_register_ids: dict[int, int] = {}

    def walk(node: Any) -> None:
        if isinstance(node, dict):
            data_item = node.get("dataItem")
            if isinstance(data_item, dict) and isinstance(data_item.get("id"), int) and node.get("enabled") is not False:
                register_id = data_item["id"]
                register_ids.add(register_id)
                if "value" in data_item:
                    values[register_id] = data_item["value"]
                if data_item.get("readOnly") is False:
                    writable_registers.add(register_id)
                extension = data_item.get("extension")
                if isinstance(extension, dict) and isinstance(extension.get("modbusRegister"), int):
                    modbus_register_ids.setdefault(extension["modbusRegister"], register_id)
            if (route := normalize_view_route(node.get("route"))) is not None:
                routes.add(route)
            for child in node.values():
                walk(child)
        elif isinstance(node, list):
            for child in node:
                walk(child)

    walk(view)
    return _HomeSolutionViewCapabilities(values, routes, register_ids, writable_registers, modbus_register_ids)


@dataclass
class HomeSolutionViewCatalog:
    """Discover and refresh all capability views exposed by one unit."""

    seed_routes: tuple[str, ...] = DEFAULT_VIEW_ROUTES
    batch_size: int = DEFAULT_VIEW_BATCH_SIZE
    max_routes: int = DEFAULT_MAX_VIEW_ROUTES
    _routes: list[str] = field(default_factory=list, init=False)
    _route_capabilities: dict[str, _HomeSolutionViewCapabilities] = field(default_factory=dict, init=False)
    _values: dict[int, Any] = field(default_factory=dict, init=False)
    _register_routes: dict[int, str] = field(default_factory=dict, init=False)
    _writable_registers: set[int] = field(default_factory=set, init=False)
    _modbus_register_ids: dict[int, int] = field(default_factory=dict, init=False)

    @property
    def routes(self) -> tuple[str, ...]:
        """Return discovered routes in stable discovery order."""
        return tuple(self._routes)

    def route_for_register(self, register_id: int) -> str | None:
        """Return the first view which exposed a register."""
        return self._register_routes.get(register_id)

    def is_register_writable(self, register_id: int) -> bool:
        """Return whether a discovered data item explicitly permits writes."""
        return register_id in self._writable_registers

    @property
    def modbus_register_ids(self) -> dict[int, int]:
        """Return a copy of the discovered zero-based Modbus-to-data-item map."""
        return dict(self._modbus_register_ids)

    def register_id_for_modbus(self, address_1based: int) -> int | None:
        """Return the cloud data-item ID backing a SAVE register address."""
        return self._modbus_register_ids.get(address_1based - 1)

    def discover(self, api: HomeSolutionViewsAPI, device_id: str) -> HomeSolutionRefreshResult:
        """Recursively discover linked capability views and their initial values."""
        self._routes.clear()
        self._route_capabilities.clear()
        self._values.clear()
        self._register_routes.clear()
        self._writable_registers.clear()
        self._modbus_register_ids.clear()
        pending = deque(filter(None, (normalize_view_route(route) for route in self.seed_routes)))
        queued = set(pending)
        errors: dict[str, str] = {}
        successful_routes: set[str] = set()

        while pending and len(self._routes) < self.max_routes:
            batch: list[str] = []
            while pending and len(batch) < self.batch_size and len(self._routes) < self.max_routes:
                route = pending.popleft()
                if route in self._routes:
                    continue
                self._routes.append(route)
                batch.append(route)
            if not batch:
                continue

            result = api.fetch_device_views(device_id, tuple(batch))
            errors.update(result.errors)
            for route in batch:
                view = result.views.get(route)
                if view is None:
                    continue
                successful_routes.add(route)
                capabilities = _extract_view_capabilities(view)
                self._route_capabilities[route] = capabilities
                for linked_route in sorted(capabilities.routes):
                    if linked_route not in queued and len(queued) < self.max_routes:
                        queued.add(linked_route)
                        pending.append(linked_route)

        self._rebuild_capabilities()
        return HomeSolutionRefreshResult(values=dict(self._values), errors=errors, successful_routes=frozenset(successful_routes))

    def refresh(self, api: HomeSolutionViewsAPI, device_id: str) -> HomeSolutionRefreshResult:
        """Refresh every discovered view once."""
        return self.refresh_routes(api, device_id, tuple(self._routes))

    def refresh_routes(
        self,
        api: HomeSolutionViewsAPI,
        device_id: str,
        routes: Iterable[str],
    ) -> HomeSolutionRefreshResult:
        """Refresh a selected set of discovered routes."""
        errors: dict[str, str] = {}
        successful_routes: set[str] = set()
        discovered_links: set[str] = set()

        for batch in self._batches(routes):
            result = api.fetch_device_views(device_id, batch)
            errors.update(result.errors)
            for route in batch:
                view = result.views.get(route)
                if view is None:
                    continue
                successful_routes.add(route)
                capabilities = _extract_view_capabilities(view)
                self._route_capabilities[route] = capabilities
                discovered_links.update(capabilities.routes)

        for route in sorted(discovered_links):
            if route not in self._routes and len(self._routes) < self.max_routes:
                self._routes.append(route)

        self._rebuild_capabilities()
        return HomeSolutionRefreshResult(values=dict(self._values), errors=errors, successful_routes=frozenset(successful_routes))

    def _rebuild_capabilities(self) -> None:
        """Rebuild aggregate indexes from authoritative per-route snapshots."""
        self._values.clear()
        self._register_routes.clear()
        self._writable_registers.clear()
        self._modbus_register_ids.clear()
        for route in self._routes:
            capabilities = self._route_capabilities.get(route)
            if capabilities is None:
                continue
            self._values.update(capabilities.values)
            self._writable_registers.update(capabilities.writable_registers)
            for register_id in capabilities.register_ids:
                self._register_routes.setdefault(register_id, route)
            for modbus_register, register_id in capabilities.modbus_register_ids.items():
                self._modbus_register_ids.setdefault(modbus_register, register_id)

    def _batches(self, routes: Iterable[str]) -> Iterable[tuple[str, ...]]:
        """Yield stable route batches bounded for one GraphQL request."""
        batch: list[str] = []
        for route in routes:
            batch.append(route)
            if len(batch) == self.batch_size:
                yield tuple(batch)
                batch.clear()
        if batch:
            yield tuple(batch)

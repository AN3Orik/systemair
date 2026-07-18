"""Systemair entity class."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import API_TYPE_HOMESOLUTION, ATTRIBUTION, DOMAIN
from .coordinator import SystemairDataUpdateCoordinator

if TYPE_CHECKING:
    from collections.abc import Iterable

    from homeassistant.core import HomeAssistant


def homesolution_supported_descriptions[DescriptionT](
    coordinator: SystemairDataUpdateCoordinator,
    descriptions: Iterable[DescriptionT],
    *,
    writable: bool = False,
    writable_32bit: bool = False,
) -> tuple[DescriptionT, ...]:
    """Keep only entities backed by a completely discovered cloud capability."""
    descriptions = tuple(descriptions)
    if not coordinator.homesolution_capabilities_complete:
        return descriptions

    supported: list[DescriptionT] = []
    for description in descriptions:
        registry = getattr(description, "registry", None)
        if registry is None:
            supported.append(description)
            continue
        if not coordinator.supports_modbus_data(registry):
            continue
        if writable and not coordinator.can_set_modbus_data(registry):
            continue
        if writable_32bit and not coordinator.can_set_modbus_data_32bit(registry):
            continue
        supported.append(description)
    return tuple(supported)


def remove_unsupported_homesolution_entities[DescriptionT](
    hass: HomeAssistant,
    coordinator: SystemairDataUpdateCoordinator,
    entity_domain: str,
    descriptions: Iterable[DescriptionT],
    supported_descriptions: Iterable[DescriptionT],
) -> None:
    """Remove stale registry entries for capabilities absent from this cloud unit."""
    if not coordinator.homesolution_capabilities_complete:
        return

    supported_keys = {description.key for description in supported_descriptions}
    registry = er.async_get(hass)
    for description in descriptions:
        if description.key in supported_keys:
            continue
        unique_id = f"{coordinator.config_entry.entry_id}-{description.key}"
        entity_id = registry.async_get_entity_id(entity_domain, DOMAIN, unique_id)
        if entity_id is not None:
            registry.async_remove(entity_id)


class SystemairEntity(CoordinatorEntity[SystemairDataUpdateCoordinator]):
    """SystemairEntity class."""

    _attr_attribution = ATTRIBUTION
    _attr_has_entity_name = True

    def __init__(self, coordinator: SystemairDataUpdateCoordinator) -> None:
        """Initialize."""
        super().__init__(coordinator)
        self._attr_unique_id = coordinator.config_entry.entry_id
        self._is_homesolution = coordinator.config_entry.data.get("api_type") == API_TYPE_HOMESOLUTION

        # Get model from user selection or device info
        model = coordinator.config_entry.runtime_data.model or coordinator.config_entry.runtime_data.mb_model

        device_info_dict = {
            "name": f"Systemair {model}" if model else "Systemair VSR",
            "manufacturer": "Systemair",
            "model": model,
            "hw_version": coordinator.config_entry.runtime_data.mb_hw_version,
            "sw_version": coordinator.config_entry.runtime_data.mb_sw_version,
            "serial_number": coordinator.config_entry.runtime_data.serial_number,
            "identifiers": {
                (
                    coordinator.config_entry.domain,
                    coordinator.config_entry.entry_id,
                ),
            },
        }

        # Add configuration URL for WebAPI devices
        if coordinator.config_entry.runtime_data.configuration_url:
            device_info_dict["configuration_url"] = coordinator.config_entry.runtime_data.configuration_url

        self._attr_device_info = DeviceInfo(**device_info_dict)

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        # Check if coordinator has data
        if self.coordinator.data is None:
            return False

        # For HomeSolution, check if the client reports the device as available
        if self._is_homesolution and hasattr(self.coordinator.client, "available"):
            if not self.coordinator.client.available:
                return False
            description = getattr(self, "entity_description", None)
            registry = getattr(description, "registry", None)
            if registry is not None:
                return self.coordinator.has_modbus_data(registry)
            return True

        # For other API types, use the default coordinator availability
        return super().available

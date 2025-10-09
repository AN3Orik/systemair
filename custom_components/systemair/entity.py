"""Systemair entity class."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTRIBUTION
from .coordinator import SystemairDataUpdateCoordinator


class SystemairEntity(CoordinatorEntity[SystemairDataUpdateCoordinator]):
    """SystemairEntity class."""

    _attr_attribution = ATTRIBUTION
    _attr_has_entity_name = True

    def __init__(self, coordinator: SystemairDataUpdateCoordinator) -> None:
        """Initialize."""
        super().__init__(coordinator)
        self._attr_unique_id = coordinator.config_entry.entry_id

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

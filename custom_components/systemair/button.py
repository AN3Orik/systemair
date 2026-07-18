"""Button platform for Systemair."""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import TYPE_CHECKING

from homeassistant.components.button import (
    ButtonDeviceClass,
    ButtonEntity,
    ButtonEntityDescription,
)
from homeassistant.const import EntityCategory
from homeassistant.exceptions import HomeAssistantError

from .const import LOGGER
from .entity import SystemairEntity
from .modbus import ModbusParameter, parameter_map
from .profiles import DEVICE_PROFILE_SAVE

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import SystemairDataUpdateCoordinator
    from .data import SystemairConfigEntry


@dataclass(kw_only=True, frozen=True)
class SystemairButtonEntityDescription(ButtonEntityDescription):
    """Describe a Systemair button and its target register."""

    registry: ModbusParameter


ENTITY_DESCRIPTIONS: tuple[SystemairButtonEntityDescription, ...] = (
    SystemairButtonEntityDescription(
        key="reset_filter_timer",
        translation_key="reset_filter_timer",
        device_class=ButtonDeviceClass.RESTART,
        entity_category=EntityCategory.CONFIG,
        registry=parameter_map["REG_FILTER_REPLACEMENT_TIME_L"],
    ),
)

# Constant from documentation for calculating timestamp
# Days from 1970-01-01 = (Time seconds - Constant) / 86400
# Time seconds = Unix timestamp + Constant
TIMESTAMP_CONSTANT = 760516096


async def async_setup_entry(
    _hass: HomeAssistant,
    entry: SystemairConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the button platform."""
    if entry.runtime_data.profile.profile_id != DEVICE_PROFILE_SAVE:
        return

    coordinator = entry.runtime_data.coordinator
    async_add_entities(SystemairButton(coordinator=coordinator, entity_description=desc) for desc in ENTITY_DESCRIPTIONS)


class SystemairButton(SystemairEntity, ButtonEntity):
    """Systemair button class."""

    def __init__(
        self,
        coordinator: SystemairDataUpdateCoordinator,
        entity_description: SystemairButtonEntityDescription,
    ) -> None:
        """Initialize the button class."""
        super().__init__(coordinator)
        self.entity_description = entity_description
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}-{entity_description.key}"

    @property
    def available(self) -> bool:
        """Return whether filter reset is supported by the active transport."""
        return super().available and self.coordinator.can_set_modbus_data_32bit(self.entity_description.registry)

    async def async_press(self) -> None:
        """Handle the button press."""
        if self.entity_description.key == "reset_filter_timer":
            LOGGER.info("Resetting filter timer by writing current timestamp.")
            try:
                device_timestamp = int(time.time()) + TIMESTAMP_CONSTANT
                await self.coordinator.async_set_modbus_data_32bit(self.entity_description.registry, device_timestamp)
            except Exception as exc:
                LOGGER.error("Failed to reset filter timer: %s", exc)
                raise HomeAssistantError from exc

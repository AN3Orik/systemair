"""Select platform for Systemair."""

from __future__ import annotations

import asyncio
import asyncio.exceptions
from dataclasses import dataclass
from typing import TYPE_CHECKING

from homeassistant.components.select import SelectEntity, SelectEntityDescription
from homeassistant.const import EntityCategory
from homeassistant.exceptions import HomeAssistantError

from .entity import SystemairEntity
from .modbus import ModbusParameter, parameter_map

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import SystemairDataUpdateCoordinator
    from .data import SystemairConfigEntry


@dataclass(kw_only=True, frozen=True)
class SystemairSelectEntityDescription(SelectEntityDescription):
    """Describes a Systemair select entity."""

    registry: ModbusParameter
    options_map: dict[int, str]


ENTITY_DESCRIPTIONS = (
    SystemairSelectEntityDescription(
        key="temperature_control_mode",
        translation_key="temperature_control_mode",
        icon="mdi:thermostat",
        entity_category=EntityCategory.CONFIG,
        registry=parameter_map["REG_TC_CONTROL_MODE"],
        options_map={
            0: "supply_air",
            1: "room_air",
            2: "extract_air",
        },
    ),
    SystemairSelectEntityDescription(
        key="fan_regulation_unit",
        translation_key="fan_regulation_unit",
        icon="mdi:fan-speed-1",
        entity_category=EntityCategory.CONFIG,
        registry=parameter_map["REG_FAN_REGULATION_UNIT"],
        options_map={
            0: "manual_percent",
            1: "manual_rpm",
            2: "pressure",
            3: "flow",
            4: "external",
        },
    ),
    SystemairSelectEntityDescription(
        key="defrosting_mode",
        translation_key="defrosting_mode",
        icon="mdi:snowflake-melt",
        entity_category=EntityCategory.CONFIG,
        registry=parameter_map["REG_DEFROSTING_MODE"],
        options_map={
            0: "soft",
            1: "normal",
            2: "hard",
        },
    ),
    SystemairSelectEntityDescription(
        key="free_cooling_supply_fan_level",
        translation_key="free_cooling_supply_fan_level",
        icon="mdi:fan",
        entity_category=EntityCategory.CONFIG,
        registry=parameter_map["REG_FREE_COOLING_MIN_SPEED_LEVEL_SAF"],
        options_map={
            3: "normal",
            4: "high",
            5: "maximum",
        },
    ),
    SystemairSelectEntityDescription(
        key="free_cooling_extract_fan_level",
        translation_key="free_cooling_extract_fan_level",
        icon="mdi:fan",
        entity_category=EntityCategory.CONFIG,
        registry=parameter_map["REG_FREE_COOLING_MIN_SPEED_LEVEL_EAF"],
        options_map={
            3: "normal",
            4: "high",
            5: "maximum",
        },
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001
    entry: SystemairConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the select platform."""
    async_add_entities(
        SystemairSelect(
            coordinator=entry.runtime_data.coordinator,
            entity_description=entity_description,
        )
        for entity_description in ENTITY_DESCRIPTIONS
    )


class SystemairSelect(SystemairEntity, SelectEntity):
    """Systemair select class."""

    entity_description: SystemairSelectEntityDescription

    def __init__(
        self,
        coordinator: SystemairDataUpdateCoordinator,
        entity_description: SystemairSelectEntityDescription,
    ) -> None:
        """Initialize the select class."""
        super().__init__(coordinator)
        self.entity_description = entity_description
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}-{entity_description.key}"
        self._attr_options = list(self.entity_description.options_map.values())
        self._option_to_value_map = {v: k for k, v in self.entity_description.options_map.items()}

    @property
    def current_option(self) -> str | None:
        """Return the selected entity option to represent the entity state."""
        value = self.coordinator.get_modbus_data(self.entity_description.registry)
        return self.entity_description.options_map.get(int(value))

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        value = self._option_to_value_map.get(option)
        if value is None:
            return

        try:
            await self.coordinator.set_modbus_data(self.entity_description.registry, value)
            await asyncio.sleep(1)
        except (asyncio.exceptions.TimeoutError, ConnectionError) as exc:
            raise HomeAssistantError from exc
        finally:
            await self.coordinator.async_refresh()

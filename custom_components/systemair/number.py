"""The Systemair integration."""

import asyncio.exceptions
from dataclasses import dataclass

from homeassistant.components.number import (
    NumberDeviceClass,
    NumberEntity,
    NumberEntityDescription,
    NumberMode,
)
from homeassistant.const import EntityCategory, UnitOfTemperature, UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .coordinator import SystemairDataUpdateCoordinator
from .data import SystemairConfigEntry
from .entity import SystemairEntity
from .modbus import ModbusParameter, parameter_map


@dataclass(kw_only=True, frozen=True)
class SystemairNumberEntityDescription(NumberEntityDescription):
    """Describes a Systemair number entity."""

    registry: ModbusParameter


NUMBERS: tuple[SystemairNumberEntityDescription, ...] = (
    SystemairNumberEntityDescription(
        key="time_delay_holiday",
        translation_key="time_delay_holiday",
        entity_category=EntityCategory.CONFIG,
        device_class=NumberDeviceClass.DURATION,
        native_step=1,
        mode=NumberMode.SLIDER,
        native_unit_of_measurement=UnitOfTime.DAYS,
        registry=parameter_map["REG_USERMODE_HOLIDAY_TIME"],
    ),
    SystemairNumberEntityDescription(
        key="time_delay_away",
        translation_key="time_delay_away",
        entity_category=EntityCategory.CONFIG,
        device_class=NumberDeviceClass.DURATION,
        native_step=1,
        mode=NumberMode.SLIDER,
        native_unit_of_measurement=UnitOfTime.HOURS,
        registry=parameter_map["REG_USERMODE_AWAY_TIME"],
    ),
    SystemairNumberEntityDescription(
        key="time_delay_fireplace",
        translation_key="time_delay_fireplace",
        entity_category=EntityCategory.CONFIG,
        device_class=NumberDeviceClass.DURATION,
        native_step=1,
        mode=NumberMode.SLIDER,
        native_unit_of_measurement=UnitOfTime.MINUTES,
        registry=parameter_map["REG_USERMODE_FIREPLACE_TIME"],
    ),
    SystemairNumberEntityDescription(
        key="time_delay_refresh",
        translation_key="time_delay_refresh",
        entity_category=EntityCategory.CONFIG,
        device_class=NumberDeviceClass.DURATION,
        native_step=1,
        mode=NumberMode.SLIDER,
        native_unit_of_measurement=UnitOfTime.MINUTES,
        registry=parameter_map["REG_USERMODE_REFRESH_TIME"],
    ),
    SystemairNumberEntityDescription(
        key="time_delay_crowded",
        translation_key="time_delay_crowded",
        entity_category=EntityCategory.CONFIG,
        device_class=NumberDeviceClass.DURATION,
        native_step=1,
        mode=NumberMode.SLIDER,
        native_unit_of_measurement=UnitOfTime.HOURS,
        registry=parameter_map["REG_USERMODE_CROWDED_TIME"],
    ),
    SystemairNumberEntityDescription(
        key="filter_period",
        translation_key="filter_period",
        entity_category=EntityCategory.CONFIG,
        icon="mdi:filter-cog",
        native_step=1,
        mode=NumberMode.SLIDER,
        native_unit_of_measurement=UnitOfTime.MONTHS,
        registry=parameter_map["REG_FILTER_PERIOD"],
    ),
    SystemairNumberEntityDescription(
        key="eco_mode_temperature_offset",
        translation_key="eco_mode_temperature_offset",
        entity_category=EntityCategory.CONFIG,
        device_class=NumberDeviceClass.TEMPERATURE,
        native_step=0.1,
        mode=NumberMode.BOX,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        registry=parameter_map["REG_ECO_T_Y1_OFFSET"],
    ),
)


async def async_setup_entry(
    _hass: HomeAssistant,
    entry: SystemairConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up number from a config entry."""
    async_add_entities(
        SystemairNumber(
            coordinator=entry.runtime_data.coordinator,
            entity_description=entity_description,
        )
        for entity_description in NUMBERS
    )


class SystemairNumber(SystemairEntity, NumberEntity):
    """Representation of a Systemair Number."""

    _attr_has_entity_name = True

    entity_description: SystemairNumberEntityDescription

    def __init__(
        self,
        coordinator: SystemairDataUpdateCoordinator,
        entity_description: SystemairNumberEntityDescription,
    ) -> None:
        """Initialize the number class."""
        super().__init__(coordinator)

        self.entity_description = entity_description
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}-{entity_description.key}"
        self.native_min_value = float(entity_description.registry.min_value or 0)
        self.native_max_value = float(entity_description.registry.max_value or 100)

    @property
    def native_value(self) -> float:
        """Return the state of the number."""
        return self.coordinator.get_modbus_data(self.entity_description.registry)

    async def async_set_native_value(self, value: float) -> None:
        """Update the current value."""
        try:
            await self.coordinator.set_modbus_data(self.entity_description.registry, value)
        except (asyncio.exceptions.TimeoutError, ConnectionError) as exc:
            raise HomeAssistantError from exc
        finally:
            await self.coordinator.async_refresh()

"""Binary sensor platform for Systemair."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)

from .entity import SystemairEntity
from .modbus import ModbusParameter, parameter_map

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import SystemairDataUpdateCoordinator
    from .data import SystemairConfigEntry


@dataclass(kw_only=True, frozen=True)
class SystemairBinarySensorEntityDescription(BinarySensorEntityDescription):
    """Describes a Systemair binary sensor entity."""

    registry: ModbusParameter


ENTITY_DESCRIPTIONS = (
    SystemairBinarySensorEntityDescription(
        key="heat_exchange_active",
        translation_key="heat_exchange_active",
        device_class=BinarySensorDeviceClass.RUNNING,
        registry=parameter_map["REG_OUTPUT_Y2_DIGITAL"],
    ),
    SystemairBinarySensorEntityDescription(
        key="heater_active",
        translation_key="heater_active",
        device_class=BinarySensorDeviceClass.RUNNING,
        registry=parameter_map["REG_OUTPUT_TRIAC"],
    ),
    SystemairBinarySensorEntityDescription(
        key="heat_recovery_active",
        translation_key="heat_recovery_active",
        device_class=BinarySensorDeviceClass.RUNNING,
        registry=parameter_map["REG_FUNCTION_ACTIVE_HEAT_RECOVERY"],
    ),
    SystemairBinarySensorEntityDescription(
        key="cool_recovery_active",
        translation_key="cool_recovery_active",
        device_class=BinarySensorDeviceClass.RUNNING,
        registry=parameter_map["REG_FUNCTION_ACTIVE_COOLING_RECOVERY"],
    ),
    SystemairBinarySensorEntityDescription(
        key="free_cooling_active",
        translation_key="free_cooling_active",
        device_class=BinarySensorDeviceClass.RUNNING,
        registry=parameter_map["REG_FUNCTION_ACTIVE_FREE_COOLING"],
    ),
    SystemairBinarySensorEntityDescription(
        key="defrosting_active",
        translation_key="defrosting_active",
        device_class=BinarySensorDeviceClass.RUNNING,
        registry=parameter_map["REG_FUNCTION_ACTIVE_DEFROSTING"],
    ),
    SystemairBinarySensorEntityDescription(
        key="moisture_transfer_active",
        translation_key="moisture_transfer_active",
        device_class=BinarySensorDeviceClass.RUNNING,
        registry=parameter_map["REG_FUNCTION_ACTIVE_MOISTURE_TRANSFER"],
    ),
    SystemairBinarySensorEntityDescription(
        key="secondary_air_active",
        translation_key="secondary_air_active",
        device_class=BinarySensorDeviceClass.RUNNING,
        registry=parameter_map["REG_FUNCTION_ACTIVE_SECONDARY_AIR"],
    ),
    SystemairBinarySensorEntityDescription(
        key="vacuum_cleaner_active",
        translation_key="vacuum_cleaner_active",
        device_class=BinarySensorDeviceClass.RUNNING,
        registry=parameter_map["REG_FUNCTION_ACTIVE_VACUUM_CLEANER"],
    ),
    SystemairBinarySensorEntityDescription(
        key="cooker_hood_active",
        translation_key="cooker_hood_active",
        device_class=BinarySensorDeviceClass.RUNNING,
        registry=parameter_map["REG_FUNCTION_ACTIVE_COOKER_HOOD"],
    ),
    SystemairBinarySensorEntityDescription(
        key="heating_active",
        translation_key="heating_active",
        device_class=BinarySensorDeviceClass.RUNNING,
        registry=parameter_map["REG_FUNCTION_ACTIVE_HEATING"],
    ),
    SystemairBinarySensorEntityDescription(
        key="heater_cool_down_active",
        translation_key="heater_cool_down_active",
        device_class=BinarySensorDeviceClass.RUNNING,
        registry=parameter_map["REG_FUNCTION_ACTIVE_HEATER_COOL_DOWN"],
    ),
    SystemairBinarySensorEntityDescription(
        key="heater_digital_output",
        translation_key="heater_digital_output",
        device_class=BinarySensorDeviceClass.RUNNING,
        registry=parameter_map["REG_OUTPUT_Y1_DIGITAL"],
    ),
    SystemairBinarySensorEntityDescription(
        key="emergency_thermostat",
        translation_key="emergency_thermostat",
        device_class=BinarySensorDeviceClass.PROBLEM,
        registry=parameter_map["REG_SENSOR_EMT"],
    ),
    SystemairBinarySensorEntityDescription(
        key="heating_circ_pump",
        translation_key="heating_circ_pump",
        device_class=BinarySensorDeviceClass.RUNNING,
        registry=parameter_map["REG_OUTPUT_Y1_CIRC_PUMP"],
    ),
    SystemairBinarySensorEntityDescription(
        key="cooling_circ_pump",
        translation_key="cooling_circ_pump",
        device_class=BinarySensorDeviceClass.RUNNING,
        registry=parameter_map["REG_OUTPUT_Y3_CIRC_PUMP"],
    ),
    SystemairBinarySensorEntityDescription(
        key="changeover_circ_pump",
        translation_key="changeover_circ_pump",
        device_class=BinarySensorDeviceClass.RUNNING,
        registry=parameter_map["REG_OUTPUT_Y1_Y3_CIRC_PUMP"],
    ),
    SystemairBinarySensorEntityDescription(
        key="extra_controller_circ_pump",
        translation_key="extra_controller_circ_pump",
        device_class=BinarySensorDeviceClass.RUNNING,
        registry=parameter_map["REG_OUTPUT_Y4_CIRC_PUMP"],
    ),
    SystemairBinarySensorEntityDescription(
        key="changeover_feedback",
        translation_key="changeover_feedback",
        device_class=BinarySensorDeviceClass.RUNNING,
        registry=parameter_map["REG_SENSOR_DI_CHANGE_OVER_FEEDBACK"],
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001 Unused function argument: `hass`
    entry: SystemairConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the binary_sensor platform."""
    async_add_entities(
        SystemairBinarySensor(
            coordinator=entry.runtime_data.coordinator,
            entity_description=entity_description,
        )
        for entity_description in ENTITY_DESCRIPTIONS
    )


class SystemairBinarySensor(SystemairEntity, BinarySensorEntity):
    """Systemair binary_sensor class."""

    entity_description: SystemairBinarySensorEntityDescription

    def __init__(
        self,
        coordinator: SystemairDataUpdateCoordinator,
        entity_description: SystemairBinarySensorEntityDescription,
    ) -> None:
        """Initialize the binary_sensor class."""
        super().__init__(coordinator)
        self.entity_description = entity_description
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}-{entity_description.key}"

    @property
    def is_on(self) -> bool:
        """Return true if the binary_sensor is on."""
        return self.coordinator.get_modbus_data(self.entity_description.registry) != 0

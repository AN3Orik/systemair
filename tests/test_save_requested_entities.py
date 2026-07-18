"""Tests for requested SAVE status entities."""

# ruff: noqa: S101

from __future__ import annotations

import unittest

from homeassistant.const import PERCENTAGE

from custom_components.systemair import binary_sensor as binary_sensor_module
from custom_components.systemair import sensor as sensor_module

PRESSURE_GUARD_MODE = 12


class FakeCoordinator:
    """Expose one register value to a binary sensor."""

    def __init__(self, value: int | None) -> None:
        """Store the value returned for the entity register."""
        self.value = value

    def get_modbus_data(self, _register: object) -> int | None:
        """Return the configured register value."""
        return self.value


def binary_sensor_entity(key: str, value: int | None) -> object:
    """Create a binary sensor without Home Assistant initialization."""
    entity_class = binary_sensor_module.SystemairBinarySensor
    description = next(description for description in binary_sensor_module.ENTITY_DESCRIPTIONS if description.key == key)
    entity = entity_class.__new__(entity_class)
    entity.coordinator = FakeCoordinator(value)
    entity.entity_description = description
    return entity


class SaveRequestedEntitiesTest(unittest.TestCase):
    """The requested entities use the documented SAVE registers."""

    def test_requested_entity_descriptions(self) -> None:
        """Heat exchanger, ECO, and Pressure Guard use their source registers."""
        sensor_descriptions = {description.key: description for description in sensor_module.ENTITY_DESCRIPTIONS}
        binary_sensor_descriptions = {description.key: description for description in binary_sensor_module.ENTITY_DESCRIPTIONS}

        heat_exchanger = sensor_descriptions.get("heat_exchanger_output")
        eco_function = binary_sensor_descriptions.get("eco_function_active")
        pressure_guard = binary_sensor_descriptions.get("pressure_guard_active")

        assert heat_exchanger is not None
        assert heat_exchanger.registry.short == "REG_OUTPUT_Y2_ANALOG"
        assert heat_exchanger.native_unit_of_measurement == PERCENTAGE

        assert eco_function is not None
        assert eco_function.registry.short == "REG_ECO_FUNCTION_ACTIVE"

        assert pressure_guard is not None
        assert pressure_guard.registry.short == "REG_USERMODE_MODE"
        assert pressure_guard.active_value == PRESSURE_GUARD_MODE

    def test_requested_binary_sensor_states(self) -> None:
        """ECO uses its flag while Pressure Guard only matches mode 12."""
        assert binary_sensor_entity("eco_function_active", 0).is_on is False
        assert binary_sensor_entity("eco_function_active", 1).is_on is True

        expected_pressure_guard_states = {
            None: None,
            0: False,
            3: False,
            PRESSURE_GUARD_MODE: True,
        }
        for value, expected in expected_pressure_guard_states.items():
            with self.subTest(value=value):
                assert binary_sensor_entity("pressure_guard_active", value).is_on == expected


if __name__ == "__main__":
    unittest.main()

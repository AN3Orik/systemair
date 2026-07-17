"""Tests for context-aware Auto mode source diagnostics."""

# ruff: noqa: PT009

from __future__ import annotations

import unittest
from types import SimpleNamespace

from custom_components.systemair import sensor as sensor_module
from custom_components.systemair.profiles.save import SAVE_PROFILE


class FakeCoordinator:
    """Minimal coordinator exposing Auto source and active user mode registers."""

    def __init__(self, active_user_mode: int) -> None:
        """Store the controller states used by the diagnostic sensor."""
        self.data = {}
        self.config_entry = SimpleNamespace(
            entry_id="test-entry",
            options={},
            runtime_data=SimpleNamespace(profile=SAVE_PROFILE),
        )
        self._values = {
            "REG_DEMC_AUTO_MODE_SOURCE": 3,
            "REG_USERMODE_MODE": active_user_mode,
        }

    def get_modbus_data(self, register: object) -> int | None:
        """Return the configured value by register short name."""
        return self._values.get(register.short)


def auto_mode_source_sensor(active_user_mode: int) -> object:
    """Create the diagnostic sensor without Home Assistant initialization."""
    sensor_class = sensor_module.SystemairSensor
    description = next(desc for desc in sensor_module.ENTITY_DESCRIPTIONS if desc.key == "auto_mode_source")
    entity = sensor_class.__new__(sensor_class)
    entity.coordinator = FakeCoordinator(active_user_mode)
    entity.entity_description = description
    return entity


class AutoModeSourceTest(unittest.TestCase):
    """Auto source diagnostics distinguish unused Auto from a real fault."""

    def test_configuration_fault_is_not_configured_outside_auto(self) -> None:
        """An unconfigured Auto source is informational while Manual is active."""
        self.assertEqual(auto_mode_source_sensor(active_user_mode=1).native_value, "Auto mode not configured")

    def test_configuration_fault_remains_fault_in_auto(self) -> None:
        """The controller fault remains visible when Auto is actually active."""
        self.assertEqual(auto_mode_source_sensor(active_user_mode=0).native_value, "Configuration fault")

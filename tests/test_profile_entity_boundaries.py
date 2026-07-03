"""Tests that SAVE and D24810 entity metadata do not cross register maps."""

from __future__ import annotations

import unittest

from custom_components.systemair.binary_sensor import _profile_binary_sensor_descriptions
from custom_components.systemair.modbus import parameter_map
from custom_components.systemair.profiles.d24810 import D24810_PROFILE, d24810_parameter_map
from custom_components.systemair.profiles.save import SAVE_PROFILE
from custom_components.systemair.sensor import ENTITY_DESCRIPTIONS, _profile_sensor_descriptions


class ProfileEntityBoundariesTest(unittest.TestCase):
    """Entity descriptions must reference only their profile registry."""

    def test_d24810_sensor_entities_reference_d24810_registry(self) -> None:
        """D24810 sensor metadata references D24810 registers only."""
        for desc in D24810_PROFILE.entities.sensors:
            with self.subTest(key=desc.key):
                assert desc.register_key in d24810_parameter_map  # noqa: S101
                assert desc.register_key not in parameter_map  # noqa: S101

    def test_d24810_binary_sensor_entities_reference_d24810_registry(self) -> None:
        """D24810 binary sensor metadata references D24810 registers only."""
        for desc in D24810_PROFILE.entities.binary_sensors:
            with self.subTest(key=desc.key):
                assert desc.register_key in d24810_parameter_map  # noqa: S101

    def test_save_sensor_descriptions_remain_the_existing_descriptions(self) -> None:
        """SAVE keeps the current sensor description tuple unchanged."""
        assert _profile_sensor_descriptions(SAVE_PROFILE) is ENTITY_DESCRIPTIONS  # noqa: S101

    def test_d24810_sensor_descriptions_use_d24810_registry(self) -> None:
        """D24810 sensor platform descriptions are converted from profile metadata."""
        descriptions = _profile_sensor_descriptions(D24810_PROFILE)
        registry_keys = {desc.registry.short for desc in descriptions if desc.registry is not None}

        assert "REG_FAN_SF_RPM" in registry_keys  # noqa: S101
        assert "REG_SENSOR_RPM_SAF" not in registry_keys  # noqa: S101

    def test_d24810_binary_sensor_descriptions_use_d24810_registry(self) -> None:
        """D24810 binary sensor platform descriptions are converted from profile metadata."""
        descriptions = _profile_binary_sensor_descriptions(D24810_PROFILE)
        registry_keys = {desc.registry.short for desc in descriptions}

        assert registry_keys == {"REG_FAN_ALLOW_MANUAL_STOP"}  # noqa: S101

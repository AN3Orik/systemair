"""Tests that SAVE and D24810 entity metadata do not cross register maps."""

from __future__ import annotations

import unittest

from custom_components.systemair.binary_sensor import _profile_binary_sensor_descriptions
from custom_components.systemair.modbus import parameter_map
from custom_components.systemair.number import NUMBERS, _profile_number_descriptions
from custom_components.systemair.profiles.base import DeviceProfile, ProfileEntityDescriptions
from custom_components.systemair.profiles.d24810 import D24810_PROFILE, d24810_parameter_map
from custom_components.systemair.profiles.entities import (
    BinarySensorProfileEntity,
    NumberProfileEntity,
    SelectProfileEntity,
    SensorProfileEntity,
    SwitchProfileEntity,
)
from custom_components.systemair.profiles.save import SAVE_PROFILE
from custom_components.systemair.select import ENTITY_DESCRIPTIONS as SELECT_DESCRIPTIONS
from custom_components.systemair.select import _profile_select_descriptions
from custom_components.systemair.sensor import ENTITY_DESCRIPTIONS, _profile_sensor_descriptions
from custom_components.systemair.switch import ENTITY_DESCRIPTIONS as SWITCH_DESCRIPTIONS
from custom_components.systemair.switch import _profile_switch_descriptions


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

    def test_d24810_select_switch_number_entities_reference_d24810_registry(self) -> None:
        """D24810 control metadata references D24810 registers only."""
        for group in (D24810_PROFILE.entities.selects, D24810_PROFILE.entities.switches, D24810_PROFILE.entities.numbers):
            for desc in group:
                with self.subTest(key=desc.key):
                    assert desc.register_key in d24810_parameter_map  # noqa: S101

    def test_save_control_descriptions_remain_the_existing_descriptions(self) -> None:
        """SAVE keeps current select, switch, and number description tuples unchanged."""
        assert _profile_select_descriptions(SAVE_PROFILE) is SELECT_DESCRIPTIONS  # noqa: S101
        assert _profile_switch_descriptions(SAVE_PROFILE) is SWITCH_DESCRIPTIONS  # noqa: S101
        assert _profile_number_descriptions(SAVE_PROFILE) is NUMBERS  # noqa: S101

    def test_d24810_control_descriptions_use_d24810_registry(self) -> None:
        """D24810 control platform descriptions are converted from profile metadata."""
        select_registers = {desc.registry.short for desc in _profile_select_descriptions(D24810_PROFILE)}
        switch_registers = {desc.registry.short for desc in _profile_switch_descriptions(D24810_PROFILE)}
        number_registers = {desc.registry.short for desc in _profile_number_descriptions(D24810_PROFILE)}

        assert select_registers == {"REG_FAN_SPEED_LEVEL"}  # noqa: S101
        assert switch_registers == set()  # noqa: S101
        assert number_registers == {"REG_FILTER_PER"}  # noqa: S101

    def test_missing_profile_entity_registers_are_skipped(self) -> None:
        """A bad profile entity reference does not crash platform setup."""
        profile = DeviceProfile(
            profile_id="broken",
            name="Broken",
            supported_api_types=(),
            supported_platforms=(),
            registry={},
            read_blocks=(),
            test_register=1,
            entities=ProfileEntityDescriptions(
                sensors=(SensorProfileEntity(key="sensor", register_key="MISSING"),),
                binary_sensors=(BinarySensorProfileEntity(key="binary_sensor", register_key="MISSING"),),
                switches=(SwitchProfileEntity(key="switch", register_key="MISSING"),),
                selects=(SelectProfileEntity(key="select", register_key="MISSING", options_map={0: "off"}),),
                numbers=(NumberProfileEntity(key="number", register_key="MISSING"),),
            ),
        )

        with self.assertLogs("custom_components.systemair", level="WARNING"):
            assert _profile_sensor_descriptions(profile) == ()  # noqa: S101
            assert _profile_binary_sensor_descriptions(profile) == ()  # noqa: S101
            assert _profile_switch_descriptions(profile) == ()  # noqa: S101
            assert _profile_select_descriptions(profile) == ()  # noqa: S101
            assert _profile_number_descriptions(profile) == ()  # noqa: S101

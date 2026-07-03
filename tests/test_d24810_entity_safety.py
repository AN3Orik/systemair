"""Tests for D24810 entity metadata and writable safety."""

from __future__ import annotations

import unittest

from custom_components.systemair.profiles.d24810 import D24810_PROFILE


class D24810EntitySafetyTest(unittest.TestCase):
    """Unsafe D24810 R/W registers must not become writable entities."""

    def test_system_type_is_sensor_only(self) -> None:
        """System identity must not be exposed as a writable entity."""
        writable_register_keys = {
            *(desc.register_key for desc in D24810_PROFILE.entities.switches),
            *(desc.register_key for desc in D24810_PROFILE.entities.selects),
            *(desc.register_key for desc in D24810_PROFILE.entities.numbers),
        }

        assert "REG_SYSTEM_TYPE" not in writable_register_keys  # noqa: S101

    def test_manual_fan_speed_is_select_candidate(self) -> None:
        """Fan speed level is the curated writable select for D24810."""
        select_keys = {desc.register_key for desc in D24810_PROFILE.entities.selects}

        assert "REG_FAN_SPEED_LEVEL" in select_keys  # noqa: S101

    def test_core_measurements_are_sensor_candidates(self) -> None:
        """Core read-only measurements are curated sensor candidates."""
        sensor_keys = {desc.register_key for desc in D24810_PROFILE.entities.sensors}

        assert "REG_FAN_SF_RPM" in sensor_keys  # noqa: S101
        assert "REG_FAN_EF_RPM" in sensor_keys  # noqa: S101
        assert "REG_SYSTEM_TYPE" in sensor_keys  # noqa: S101

    def test_filter_period_is_number_candidate(self) -> None:
        """Filter replacement period is a safe writable number candidate."""
        number_keys = {desc.register_key for desc in D24810_PROFILE.entities.numbers}

        assert "REG_FILTER_PER" in number_keys  # noqa: S101

    def test_entity_metadata_references_existing_registers(self) -> None:
        """Curated entity metadata must not point at non-existent registry keys."""
        entity_groups = (
            D24810_PROFILE.entities.sensors,
            D24810_PROFILE.entities.binary_sensors,
            D24810_PROFILE.entities.switches,
            D24810_PROFILE.entities.selects,
            D24810_PROFILE.entities.numbers,
        )
        referenced = {desc.register_key for entities in entity_groups for desc in entities}

        missing = sorted(referenced.difference(D24810_PROFILE.registry))
        assert missing == []  # noqa: S101

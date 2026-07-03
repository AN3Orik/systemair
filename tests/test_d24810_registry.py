"""Tests for Legacy Residential / D24810 registry metadata."""

from __future__ import annotations

import unittest

from custom_components.systemair.const import API_TYPE_MODBUS_SERIAL, API_TYPE_MODBUS_TCP
from custom_components.systemair.modbus import RegisterType
from custom_components.systemair.profiles import DEVICE_PROFILE_LEGACY_D24810, get_device_profile
from custom_components.systemair.profiles.d24810 import D24810_PROFILE, d24810_parameter_map

D24810_PROBE_REGISTERS = {
    "REG_FAN_SPEED_LEVEL": 101,
    "REG_FAN_FLOW_UNITS": 108,
    "REG_SYSTEM_TYPE": 501,
    "REG_FILTER_PERIOD": 601,
    "REG_FILTER_DAYS": 602,
}
D24810_FAN_READ_BLOCK = (101, 14)
SAVE_FIRST_READ_BLOCK = (1001, 62)


class D24810RegistryTest(unittest.TestCase):
    """Validate critical D24810 PDF registers."""

    def test_profile_is_registered(self) -> None:
        """The D24810 profile is registered and supports only Modbus transports."""
        assert get_device_profile(DEVICE_PROFILE_LEGACY_D24810) is D24810_PROFILE  # noqa: S101
        assert D24810_PROFILE.supported_api_types == (API_TYPE_MODBUS_TCP, API_TYPE_MODBUS_SERIAL)  # noqa: S101

    def test_probe_registers_have_pdf_addresses(self) -> None:
        """D24810 probe registers use one-based PDF addresses."""
        for key, register in D24810_PROBE_REGISTERS.items():
            with self.subTest(key=key):
                assert d24810_parameter_map[key].register == register  # noqa: S101
                assert d24810_parameter_map[key].reg_type == RegisterType.Holding  # noqa: S101

    def test_system_type_is_not_writable_entity_candidate(self) -> None:
        """System type is identity/configuration, not a writable user entity."""
        assert "REG_SYSTEM_TYPE" not in D24810_PROFILE.entities.switches  # noqa: S101
        assert "REG_SYSTEM_TYPE" not in D24810_PROFILE.entities.selects  # noqa: S101
        assert "REG_SYSTEM_TYPE" not in D24810_PROFILE.entities.numbers  # noqa: S101

    def test_d24810_read_blocks_do_not_match_save_blocks(self) -> None:
        """D24810 uses legacy read blocks, not the SAVE polling map."""
        assert SAVE_FIRST_READ_BLOCK not in D24810_PROFILE.read_blocks  # noqa: S101
        assert D24810_FAN_READ_BLOCK in D24810_PROFILE.read_blocks  # noqa: S101

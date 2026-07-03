"""Tests for SAVE device profile metadata."""

from __future__ import annotations

import unittest

from custom_components.systemair.const import API_TYPE_HOMESOLUTION, API_TYPE_MODBUS_SERIAL, API_TYPE_MODBUS_TCP, API_TYPE_MODBUS_WEBAPI
from custom_components.systemair.profiles import DEVICE_PROFILE_SAVE, get_device_profile
from custom_components.systemair.profiles.save import SAVE_PROFILE

SAVE_TEST_REGISTER = 2001
SAVE_FIRST_READ_BLOCK = (1001, 62)


class SaveProfileTest(unittest.TestCase):
    """Verify the SAVE profile wraps the existing behavior."""

    def test_save_profile_is_default_compatible(self) -> None:
        """The SAVE profile exposes current SAVE registry and polling defaults."""
        assert SAVE_PROFILE.profile_id == DEVICE_PROFILE_SAVE  # noqa: S101
        assert SAVE_PROFILE.name == "SAVE"  # noqa: S101
        assert SAVE_PROFILE.test_register == SAVE_TEST_REGISTER  # noqa: S101
        assert SAVE_PROFILE.registry["REG_TC_SP"].register == SAVE_TEST_REGISTER  # noqa: S101
        assert SAVE_FIRST_READ_BLOCK in SAVE_PROFILE.read_blocks  # noqa: S101

    def test_save_profile_supports_existing_api_types(self) -> None:
        """The SAVE profile remains available to all existing API types."""
        assert SAVE_PROFILE.supported_api_types == (  # noqa: S101
            API_TYPE_MODBUS_TCP,
            API_TYPE_MODBUS_SERIAL,
            API_TYPE_MODBUS_WEBAPI,
            API_TYPE_HOMESOLUTION,
        )

    def test_profile_lookup_returns_save_profile(self) -> None:
        """Missing profile ids and explicit SAVE ids resolve to SAVE."""
        assert get_device_profile(DEVICE_PROFILE_SAVE) is SAVE_PROFILE  # noqa: S101
        assert get_device_profile(None) is SAVE_PROFILE  # noqa: S101

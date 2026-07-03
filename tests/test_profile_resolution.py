"""Tests for profile id constants and lookup behavior."""

from __future__ import annotations

import unittest

from custom_components.systemair.const import CONF_DEVICE_PROFILE
from custom_components.systemair.profiles import DEVICE_PROFILE_AUTO, DEVICE_PROFILE_SAVE, get_device_profile


class ProfileResolutionTest(unittest.TestCase):
    """Existing config entries must resolve to SAVE unless explicitly configured."""

    def test_profile_constants_are_stable(self) -> None:
        """Profile config and option ids are stable."""
        assert CONF_DEVICE_PROFILE == "device_profile"  # noqa: S101
        assert DEVICE_PROFILE_AUTO == "auto"  # noqa: S101
        assert DEVICE_PROFILE_SAVE == "save"  # noqa: S101

    def test_missing_profile_id_resolves_to_save(self) -> None:
        """Old config entries without a profile id resolve to SAVE."""
        profile = get_device_profile(None)

        assert profile.profile_id == DEVICE_PROFILE_SAVE  # noqa: S101

    def test_old_config_entry_data_resolves_to_save(self) -> None:
        """Existing entries upgraded from older versions do not need a stored profile id."""
        entry_data: dict[str, str] = {}

        profile = get_device_profile(entry_data.get(CONF_DEVICE_PROFILE))

        assert profile.profile_id == DEVICE_PROFILE_SAVE  # noqa: S101

    def test_unknown_profile_id_raises_clear_error(self) -> None:
        """Malformed profile ids must not silently fall back to a different register map."""
        try:
            get_device_profile("stale_profile")
        except ValueError:
            return
        self.fail("ValueError was not raised")

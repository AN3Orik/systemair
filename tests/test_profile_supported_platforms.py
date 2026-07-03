"""Tests for profile-supported platform lists."""

from __future__ import annotations

import unittest

from homeassistant.const import Platform

from custom_components.systemair import _profile_platforms
from custom_components.systemair.profiles.d24810 import D24810_PROFILE
from custom_components.systemair.profiles.save import SAVE_PROFILE


class ProfileSupportedPlatformsTest(unittest.TestCase):
    """Profiles expose only platforms they support."""

    def test_save_keeps_current_platforms(self) -> None:
        """SAVE profile keeps the existing platform list."""
        assert SAVE_PROFILE.supported_platforms == (  # noqa: S101
            Platform.BUTTON,
            Platform.CLIMATE,
            Platform.SENSOR,
            Platform.BINARY_SENSOR,
            Platform.SWITCH,
            Platform.NUMBER,
            Platform.SELECT,
        )

    def test_d24810_excludes_button_until_safe_action_is_confirmed(self) -> None:
        """D24810 does not forward the reset-filter button platform."""
        assert Platform.BUTTON not in D24810_PROFILE.supported_platforms  # noqa: S101
        assert Platform.CLIMATE in D24810_PROFILE.supported_platforms  # noqa: S101
        assert Platform.SENSOR in D24810_PROFILE.supported_platforms  # noqa: S101

    def test_forwarded_platforms_follow_profile(self) -> None:
        """Forwarded platforms are derived from the active profile."""
        assert _profile_platforms(SAVE_PROFILE) == list(SAVE_PROFILE.supported_platforms)  # noqa: S101
        assert _profile_platforms(D24810_PROFILE) == list(D24810_PROFILE.supported_platforms)  # noqa: S101
        assert Platform.BUTTON not in _profile_platforms(D24810_PROFILE)  # noqa: S101

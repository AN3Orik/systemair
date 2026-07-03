"""Tests for profile-supported platform lists."""

from __future__ import annotations

import unittest

from homeassistant.const import Platform

from custom_components.systemair import _profile_platforms, _profile_supports_api_type
from custom_components.systemair.const import API_TYPE_HOMESOLUTION, API_TYPE_MODBUS_SERIAL, API_TYPE_MODBUS_TCP, API_TYPE_MODBUS_WEBAPI
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

    def test_d24810_runtime_profile_is_modbus_only(self) -> None:
        """Runtime setup must reject D24810 on WebAPI/HomeSolution transports."""
        assert _profile_supports_api_type(D24810_PROFILE, API_TYPE_MODBUS_TCP)  # noqa: S101
        assert _profile_supports_api_type(D24810_PROFILE, API_TYPE_MODBUS_SERIAL)  # noqa: S101
        assert not _profile_supports_api_type(D24810_PROFILE, API_TYPE_MODBUS_WEBAPI)  # noqa: S101
        assert not _profile_supports_api_type(D24810_PROFILE, API_TYPE_HOMESOLUTION)  # noqa: S101

    def test_save_runtime_profile_supports_existing_api_types(self) -> None:
        """SAVE remains compatible with all existing transports."""
        assert _profile_supports_api_type(SAVE_PROFILE, API_TYPE_MODBUS_TCP)  # noqa: S101
        assert _profile_supports_api_type(SAVE_PROFILE, API_TYPE_MODBUS_SERIAL)  # noqa: S101
        assert _profile_supports_api_type(SAVE_PROFILE, API_TYPE_MODBUS_WEBAPI)  # noqa: S101
        assert _profile_supports_api_type(SAVE_PROFILE, API_TYPE_HOMESOLUTION)  # noqa: S101

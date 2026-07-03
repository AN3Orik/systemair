"""Tests for profile choices exposed by config flow helpers."""

from __future__ import annotations

import unittest

from custom_components.systemair.config_flow import _profile_options_for_api_type
from custom_components.systemair.const import API_TYPE_HOMESOLUTION, API_TYPE_MODBUS_SERIAL, API_TYPE_MODBUS_TCP, API_TYPE_MODBUS_WEBAPI
from custom_components.systemair.profiles import DEVICE_PROFILE_AUTO, DEVICE_PROFILE_LEGACY_D24810, DEVICE_PROFILE_SAVE

MODBUS_PROFILE_OPTIONS = (DEVICE_PROFILE_AUTO, DEVICE_PROFILE_SAVE, DEVICE_PROFILE_LEGACY_D24810)


class ConfigProfileOptionsTest(unittest.TestCase):
    """D24810 profile choices are available only for Modbus TCP and RS485."""

    def test_modbus_tcp_allows_auto_save_and_d24810(self) -> None:
        """Modbus TCP supports auto-detection and both concrete profiles."""
        assert _profile_options_for_api_type(API_TYPE_MODBUS_TCP) == MODBUS_PROFILE_OPTIONS  # noqa: S101

    def test_modbus_serial_allows_auto_save_and_d24810(self) -> None:
        """RS485 supports auto-detection and both concrete profiles."""
        assert _profile_options_for_api_type(API_TYPE_MODBUS_SERIAL) == MODBUS_PROFILE_OPTIONS  # noqa: S101

    def test_webapi_is_save_only(self) -> None:
        """WebAPI is tied to SAVE/IAM and does not support D24810."""
        assert _profile_options_for_api_type(API_TYPE_MODBUS_WEBAPI) == (DEVICE_PROFILE_SAVE,)  # noqa: S101

    def test_homesolution_is_save_only(self) -> None:
        """HomeSolution cloud is tied to SAVE and does not support D24810."""
        assert _profile_options_for_api_type(API_TYPE_HOMESOLUTION) == (DEVICE_PROFILE_SAVE,)  # noqa: S101

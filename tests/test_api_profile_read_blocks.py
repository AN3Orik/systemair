"""Tests for profile-driven Modbus client configuration."""

from __future__ import annotations

import unittest

from custom_components.systemair.api import READ_BLOCKS_ALARM_DETAILS, READ_BLOCKS_ALARM_HISTORY, READ_BLOCKS_BASE, SystemairModbusClient
from custom_components.systemair.profiles.save import SAVE_PROFILE

CUSTOM_TEST_REGISTER = 501


class ApiProfileReadBlocksTest(unittest.TestCase):
    """Verify clients preserve SAVE defaults while accepting profile read blocks."""

    def test_api_exports_save_read_blocks_for_backward_compatibility(self) -> None:
        """The legacy API read block constants still expose SAVE blocks."""
        assert tuple(READ_BLOCKS_BASE) == SAVE_PROFILE.read_blocks  # noqa: S101
        assert tuple(READ_BLOCKS_ALARM_DETAILS) == SAVE_PROFILE.alarm_detail_blocks  # noqa: S101
        assert tuple(READ_BLOCKS_ALARM_HISTORY) == SAVE_PROFILE.alarm_history_blocks  # noqa: S101

    def test_modbus_client_defaults_to_save_profile_blocks(self) -> None:
        """Modbus TCP clients use SAVE profile defaults when no profile is supplied."""
        client = SystemairModbusClient(host="127.0.0.1", port=502, slave_id=1)

        assert client.read_blocks == SAVE_PROFILE.read_blocks  # noqa: S101
        assert client.alarm_detail_blocks == SAVE_PROFILE.alarm_detail_blocks  # noqa: S101
        assert client.alarm_history_blocks == SAVE_PROFILE.alarm_history_blocks  # noqa: S101
        assert client.test_register == SAVE_PROFILE.test_register  # noqa: S101

    def test_modbus_client_accepts_custom_profile_blocks(self) -> None:
        """Modbus TCP clients can be configured with profile-specific polling."""
        client = SystemairModbusClient(
            host="127.0.0.1",
            port=502,
            slave_id=1,
            read_blocks=((101, 14),),
            alarm_detail_blocks=(),
            alarm_history_blocks=(),
            test_register=CUSTOM_TEST_REGISTER,
        )

        assert client.read_blocks == ((101, 14),)  # noqa: S101
        assert client.alarm_detail_blocks == ()  # noqa: S101
        assert client.alarm_history_blocks == ()  # noqa: S101
        assert client.test_register == CUSTOM_TEST_REGISTER  # noqa: S101

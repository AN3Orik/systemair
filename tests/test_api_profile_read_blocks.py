"""Tests for profile-driven Modbus client configuration."""

from __future__ import annotations

import unittest

from custom_components.systemair.api import (
    READ_BLOCKS_ALARM_DETAILS,
    READ_BLOCKS_ALARM_HISTORY,
    READ_BLOCKS_BASE,
    SystemairModbusClient,
    SystemairSerialClient,
)
from custom_components.systemair.profiles.save import SAVE_PROFILE

CUSTOM_TEST_REGISTER = 501


class ApiProfileReadBlocksTest(unittest.IsolatedAsyncioTestCase):
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

    def test_clients_respect_empty_blocks_and_zero_test_register_overrides(self) -> None:
        """Explicit profile overrides are not replaced by SAVE defaults when falsy."""
        clients = (
            SystemairModbusClient(
                host="127.0.0.1",
                port=502,
                slave_id=1,
                read_blocks=(),
                alarm_detail_blocks=(),
                alarm_history_blocks=(),
                test_register=0,
            ),
            SystemairSerialClient(
                port="COM1",
                read_blocks=(),
                alarm_detail_blocks=(),
                alarm_history_blocks=(),
                test_register=0,
            ),
        )

        for client in clients:
            with self.subTest(client=type(client).__name__):
                assert client.read_blocks == ()  # noqa: S101
                assert client.alarm_detail_blocks == ()  # noqa: S101
                assert client.alarm_history_blocks == ()  # noqa: S101
                assert client.test_register == 0  # noqa: S101

    async def test_modbus_client_read_registers_uses_one_based_addresses(self) -> None:
        """Modbus TCP read_registers converts one-based profile addresses to zero-based transport offsets."""
        client = SystemairModbusClient(host="127.0.0.1", port=502, slave_id=1)
        calls = []

        async def fake_queue_request(request_type: str, address: int, **kwargs: int) -> list[int]:
            calls.append((request_type, address, kwargs))
            return [42]

        client._queue_request = fake_queue_request  # noqa: SLF001

        result = await client.read_registers(501, count=2)

        assert result == [42]  # noqa: S101
        assert calls == [("read", 500, {"count": 2})]  # noqa: S101

    async def test_serial_client_read_registers_uses_one_based_addresses(self) -> None:
        """Serial read_registers converts one-based profile addresses to zero-based transport offsets."""
        client = SystemairSerialClient(port="COM1")
        calls = []

        async def fake_queue_request(request_type: str, address: int, **kwargs: int) -> list[int]:
            calls.append((request_type, address, kwargs))
            return [24]

        client._queue_request = fake_queue_request  # noqa: SLF001

        result = await client.read_registers(601, count=1)

        assert result == [24]  # noqa: S101
        assert calls == [("read", 600, {"count": 1})]  # noqa: S101

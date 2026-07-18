"""Tests for profile auto-detection config-flow behavior."""

from __future__ import annotations

import unittest
from functools import partial
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_PORT

from custom_components.systemair.config_flow import ProfileAutoDetectionFailedError, SystemairVSRConfigFlow
from custom_components.systemair.const import (
    API_TYPE_HOMESOLUTION,
    CONF_BAUDRATE,
    CONF_BYTESIZE,
    CONF_DEVICE_ID,
    CONF_DEVICE_PROFILE,
    CONF_PARITY,
    CONF_SERIAL_PORT,
    CONF_SLAVE_ID,
    CONF_STOPBITS,
    DEFAULT_BAUDRATE,
    DEFAULT_BYTESIZE,
    DEFAULT_PARITY,
    DEFAULT_STOPBITS,
)
from custom_components.systemair.profiles import DEVICE_PROFILE_AUTO, DEVICE_PROFILE_LEGACY_D24810, DEVICE_PROFILE_SAVE
from custom_components.systemair.profiles.detection import DetectionOutcome


class _FakeProfileDetectionClient:
    """Track lifecycle calls made by config-flow profile detection."""

    def __init__(self, instances: list[_FakeProfileDetectionClient], **kwargs: object) -> None:
        self.kwargs = kwargs
        self.started = False
        self.stopped = False
        instances.append(self)

    async def start(self) -> None:
        self.started = True

    async def stop(self) -> None:
        self.stopped = True


class ConfigFlowProfileDetectionTest(unittest.IsolatedAsyncioTestCase):
    """Config flow must expose auto-detection failures distinctly."""

    async def test_modbus_tcp_auto_detection_persists_detected_profile(self) -> None:
        """TCP auto-detection stores the concrete detected profile."""
        instances = []

        flow = SystemairVSRConfigFlow()
        user_input = {
            CONF_HOST: "127.0.0.1",
            CONF_PORT: 502,
            CONF_SLAVE_ID: 1,
            CONF_DEVICE_PROFILE: DEVICE_PROFILE_AUTO,
        }
        outcome = DetectionOutcome(profile_id=DEVICE_PROFILE_LEGACY_D24810, save_score=0, d24810_score=6)

        with (
            patch("custom_components.systemair.config_flow.SystemairModbusClient", partial(_FakeProfileDetectionClient, instances)),
            patch("custom_components.systemair.config_flow.async_detect_profile", AsyncMock(return_value=outcome)) as detector,
        ):
            await flow._validate_modbus_tcp_connection(user_input)  # noqa: SLF001

        assert user_input[CONF_DEVICE_PROFILE] == DEVICE_PROFILE_LEGACY_D24810  # noqa: S101
        assert instances[0].started  # noqa: S101
        assert instances[0].stopped  # noqa: S101
        detector.assert_awaited_once_with(instances[0])

    async def test_modbus_serial_auto_detection_persists_detected_profile(self) -> None:
        """RS485 auto-detection stores the concrete detected profile."""
        instances = []

        flow = SystemairVSRConfigFlow()
        user_input = {
            CONF_SERIAL_PORT: "COM1",
            CONF_BAUDRATE: str(DEFAULT_BAUDRATE),
            CONF_BYTESIZE: DEFAULT_BYTESIZE,
            CONF_PARITY: DEFAULT_PARITY,
            CONF_STOPBITS: DEFAULT_STOPBITS,
            CONF_SLAVE_ID: 1,
            CONF_DEVICE_PROFILE: DEVICE_PROFILE_AUTO,
        }
        outcome = DetectionOutcome(profile_id=DEVICE_PROFILE_SAVE, save_score=4, d24810_score=0)

        with (
            patch("custom_components.systemair.config_flow.SystemairSerialClient", partial(_FakeProfileDetectionClient, instances)),
            patch("custom_components.systemair.config_flow.async_detect_profile", AsyncMock(return_value=outcome)) as detector,
        ):
            await flow._validate_serial_connection(user_input)  # noqa: SLF001

        assert user_input[CONF_DEVICE_PROFILE] == DEVICE_PROFILE_SAVE  # noqa: S101
        assert instances[0].started  # noqa: S101
        assert instances[0].stopped  # noqa: S101
        detector.assert_awaited_once_with(instances[0])

    async def test_modbus_tcp_maps_auto_detection_failure_by_exception_type(self) -> None:
        """TCP auto-detection failure uses the dedicated error key."""
        flow = SystemairVSRConfigFlow()

        async def fail_auto_detection(_user_input: dict) -> None:
            msg = "profile detection failed"
            raise ProfileAutoDetectionFailedError(msg)

        flow._validate_modbus_tcp_connection = fail_auto_detection  # noqa: SLF001

        with self.assertLogs("custom_components.systemair", level="ERROR"):
            result = await flow.async_step_modbus_tcp(
                {
                    CONF_HOST: "127.0.0.1",
                    CONF_PORT: 502,
                    CONF_SLAVE_ID: 1,
                }
            )

        assert result["errors"]["base"] == "cannot_auto_detect_profile"  # noqa: S101

    async def test_modbus_serial_maps_auto_detection_failure_by_exception_type(self) -> None:
        """RS485 auto-detection failure uses the dedicated error key."""
        flow = SystemairVSRConfigFlow()

        async def fail_auto_detection(_user_input: dict) -> None:
            msg = "profile detection failed"
            raise ProfileAutoDetectionFailedError(msg)

        flow._validate_serial_connection = fail_auto_detection  # noqa: SLF001

        with self.assertLogs("custom_components.systemair", level="ERROR"):
            result = await flow.async_step_modbus_serial(
                {
                    CONF_SERIAL_PORT: "COM1",
                    CONF_SLAVE_ID: 1,
                }
            )

        assert result["errors"]["base"] == "cannot_auto_detect_profile"  # noqa: S101

    async def test_homesolution_reauth_accepts_legacy_id_when_identifier_is_also_present(self) -> None:
        """Existing entries can match either cloud device identifier field."""
        flow = SystemairVSRConfigFlow()
        flow._get_homesolution_devices = AsyncMock(  # noqa: SLF001
            return_value=[{"identifier": "current-identifier", "id": "legacy-device-id"}]
        )

        await flow._validate_homesolution_reauth({}, "legacy-device-id")  # noqa: SLF001

    async def test_homesolution_reauth_preserves_no_devices_error(self) -> None:
        """An account without units receives its specific translated error."""
        flow = SystemairVSRConfigFlow()
        flow._reauth_entry_data = {}  # noqa: SLF001
        entry = SimpleNamespace(
            data={"api_type": API_TYPE_HOMESOLUTION, CONF_DEVICE_ID: "device"},
            entry_id="entry",
        )
        flow._get_reauth_entry = lambda: entry  # noqa: SLF001
        flow._validate_homesolution_reauth = AsyncMock(side_effect=ValueError("no_devices_found"))  # noqa: SLF001

        result = await flow.async_step_reauth_confirm({CONF_PASSWORD: "password"})

        assert result["errors"]["base"] == "no_devices_found"  # noqa: S101

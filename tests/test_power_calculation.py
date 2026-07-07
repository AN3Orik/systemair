"""Tests for SAVE calculated power sensors."""

from __future__ import annotations

import unittest
from types import SimpleNamespace
from unittest.mock import patch

from custom_components.systemair.profiles.d24810 import D24810_PROFILE
from custom_components.systemair.profiles.save import SAVE_PROFILE
from custom_components.systemair.sensor import POWER_SENSORS, SystemairPowerSensor

VSR500_LOW_EXPECTATIONS = {
    "supply_fan_power": 60.9,
    "extract_fan_power": 55.5,
    "total_power": 132.3,
}
VSR500_REFRESH_EXPECTATIONS = {
    "supply_fan_power": 311.0,
    "extract_fan_power": 311.0,
    "total_power": 637.9,
}
VSR500_IDLE_EXPECTATIONS = {
    "supply_fan_power": 0.0,
    "extract_fan_power": 0.0,
    "total_power": 16.0,
}
SINGLE_FAN_EXPECTATIONS = {
    "supply_fan_power": 21.5,
    "extract_fan_power": 0.0,
    "total_power": 37.5,
}
D24810_HALF_HEATER_TOTAL_POWER = 851.0
D24810_VR400DE_HALF_HEATER_TOTAL_POWER = 1062.6
CONFIRMED_MODEL_HALF_HEATER_EXPECTATIONS = {
    "VR 400 DCV/B": 1060.8,
    "VR 400 DC": 1062.6,
    "VR 400 DE": 1062.6,
    "VR 700 DCV": 1292.6,
    "VR 700 DC": 1303.6,
    "VTR 200/B L 500W": 424.2,
    "VTR 200/B R 500W": 424.2,
    "VTR 200/B L 1000W": 674.2,
    "VTR 200/B R 1000W": 674.2,
}


class FakeCoordinator:
    """Minimal coordinator for calculated power sensor business logic."""

    def __init__(
        self,
        model: str,
        *,
        saf_pct: int | None,
        eaf_pct: int | None,
        heater: int = 0,
        profile: object = SAVE_PROFILE,
    ) -> None:
        """Store the minimal coordinator state needed by calculated sensors."""
        self.data = {}
        self.config_entry = SimpleNamespace(runtime_data=SimpleNamespace(model=model, profile=profile))
        self._values = {
            "REG_OUTPUT_SAF": saf_pct,
            "REG_OUTPUT_EAF": eaf_pct,
            "REG_OUTPUT_TRIAC": heater,
            "REG_FAN_SF_PWM": saf_pct,
            "REG_FAN_EF_PWM": eaf_pct,
            "REG_HC_WH_SIGNAL": heater,
        }

    def get_modbus_data(self, register: object) -> int | None:
        """Return a fake Modbus register value by short register name."""
        return self._values.get(register.short)


def power_sensor(key: str, coordinator: FakeCoordinator) -> SystemairPowerSensor:
    """Create a power sensor without Home Assistant entity initialization."""
    entity = SystemairPowerSensor.__new__(SystemairPowerSensor)
    entity.coordinator = coordinator
    entity.entity_description = next(desc for desc in POWER_SENSORS if desc.key == key)
    return entity


class PowerCalculationTest(unittest.TestCase):
    """Power calculation uses measured fan curve parameters."""

    def test_vsr500_low_power_uses_nonlinear_per_fan_curve(self) -> None:
        """VSR500 low mode matches measured SAF/EAF output percentages."""
        coordinator = FakeCoordinator("VSR 500", saf_pct=46, eaf_pct=44)

        for key, expected in VSR500_LOW_EXPECTATIONS.items():
            with self.subTest(key=key):
                assert power_sensor(key, coordinator).native_value == expected  # noqa: S101

    def test_vsr500_refresh_power_uses_each_fan_at_full_output(self) -> None:
        """VSR500 refresh mode counts one supply and one extract fan."""
        coordinator = FakeCoordinator("VSR 500", saf_pct=100, eaf_pct=100)

        for key, expected in VSR500_REFRESH_EXPECTATIONS.items():
            with self.subTest(key=key):
                assert power_sensor(key, coordinator).native_value == expected  # noqa: S101

    def test_idle_total_power_keeps_base_load_when_fans_are_stopped(self) -> None:
        """Stopped fans still expose measured controller standby consumption."""
        coordinator = FakeCoordinator("VSR 500", saf_pct=0, eaf_pct=0)

        for key, expected in VSR500_IDLE_EXPECTATIONS.items():
            with self.subTest(key=key):
                assert power_sensor(key, coordinator).native_value == expected  # noqa: S101

    def test_single_fan_model_uses_only_configured_fan_side(self) -> None:
        """Single-fan models do not split fan_power across missing fans."""
        specs = {
            "Single Fan Test": {
                "fan_power": 100,
                "heater_power": 0,
                "supply_fans": 1,
                "extract_fans": 0,
            }
        }
        coordinator = FakeCoordinator("Single Fan Test", saf_pct=50, eaf_pct=100)

        with patch("custom_components.systemair.sensor.MODEL_SPECS", specs):
            for key, expected in SINGLE_FAN_EXPECTATIONS.items():
                with self.subTest(key=key):
                    assert power_sensor(key, coordinator).native_value == expected  # noqa: S101

    def test_missing_required_fan_output_keeps_power_unknown(self) -> None:
        """Two-fan models need both fan output values before estimating total power."""
        coordinator = FakeCoordinator("VSR 500", saf_pct=46, eaf_pct=None)

        assert power_sensor("total_power", coordinator).native_value is None  # noqa: S101

    def test_d24810_power_uses_profile_fan_pwm_registers(self) -> None:
        """D24810 power calculation uses legacy PWM register aliases."""
        coordinator = FakeCoordinator("VSR500", saf_pct=46, eaf_pct=44, profile=D24810_PROFILE)

        for key, expected in VSR500_LOW_EXPECTATIONS.items():
            with self.subTest(key=key):
                assert power_sensor(key, coordinator).native_value == expected  # noqa: S101

    def test_d24810_heater_output_is_scaled_by_percentage(self) -> None:
        """D24810 heater power uses analog heater output percentage."""
        coordinator = FakeCoordinator("VSR 500", saf_pct=0, eaf_pct=0, heater=50, profile=D24810_PROFILE)

        assert power_sensor("total_power", coordinator).native_value == D24810_HALF_HEATER_TOTAL_POWER  # noqa: S101

    def test_d24810_power_uses_confirmed_vr400de_model_spec(self) -> None:
        """D24810 VR400DE uses confirmed VR 400 DC/DE fan and heater ratings."""
        coordinator = FakeCoordinator("VR400DE", saf_pct=100, eaf_pct=100, heater=50, profile=D24810_PROFILE)

        assert power_sensor("total_power", coordinator).native_value == D24810_VR400DE_HALF_HEATER_TOTAL_POWER  # noqa: S101

    def test_confirmed_model_specs_drive_power_calculation(self) -> None:
        """Confirmed model specs are available for calculated power sensors."""
        for model, expected in CONFIRMED_MODEL_HALF_HEATER_EXPECTATIONS.items():
            coordinator = FakeCoordinator(model, saf_pct=100, eaf_pct=100, heater=50, profile=D24810_PROFILE)

            with self.subTest(model=model):
                assert power_sensor("total_power", coordinator).native_value == expected  # noqa: S101

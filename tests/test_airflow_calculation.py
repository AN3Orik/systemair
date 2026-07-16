"""Tests for calculated whole-unit airflow sensors."""

# ruff: noqa: PT009

from __future__ import annotations

import unittest
from types import SimpleNamespace

from custom_components.systemair import config_flow as config_flow_module
from custom_components.systemair import sensor as sensor_module
from custom_components.systemair.profiles.d24810 import D24810_PROFILE
from custom_components.systemair.profiles.save import SAVE_PROFILE

VSR500_MAX_AIRFLOW = 609
VSR500_SUPPLY_AIRFLOW_AT_46_PERCENT = 280
VSR500_EXTRACT_AIRFLOW_AT_44_PERCENT = 268
CALIBRATED_SUPPLY_AIRFLOW_AT_46_PERCENT = 322
CALIBRATED_EXTRACT_AIRFLOW_AT_44_PERCENT = 220


def calculate_airflow(max_airflow_m3h: float | None, fan_output_percentage: float | None) -> int | None:
    """Call the production airflow calculation when it is available."""
    implementation = getattr(sensor_module, "calculate_airflow", None)
    if implementation is None:
        return -1
    return implementation(max_airflow_m3h, fan_output_percentage)


class FakeCoordinator:
    """Minimal coordinator for calculated airflow sensor business logic."""

    def __init__(
        self,
        model: str,
        *,
        saf_pct: int | None,
        eaf_pct: int | None,
        profile: object = SAVE_PROFILE,
        options: dict[str, float] | None = None,
    ) -> None:
        """Store live fan outputs, selected model, and calibration options."""
        self.data = {}
        self.config_entry = SimpleNamespace(
            entry_id="test-entry",
            options=options or {},
            runtime_data=SimpleNamespace(model=model, profile=profile),
        )
        self._values = {
            "REG_OUTPUT_SAF": saf_pct,
            "REG_OUTPUT_EAF": eaf_pct,
            "REG_FAN_SF_PWM": saf_pct,
            "REG_FAN_EF_PWM": eaf_pct,
        }

    def get_modbus_data(self, register: object) -> int | None:
        """Return a fake Modbus register value by short register name."""
        return self._values.get(register.short)


def airflow_sensor(key: str, coordinator: FakeCoordinator) -> object:
    """Create an airflow sensor without Home Assistant entity initialization."""
    sensor_class = sensor_module.SystemairAirflowSensor
    descriptions = getattr(sensor_module, "AIRFLOW_SENSORS", ())
    description = next(desc for desc in descriptions if desc.key == key)
    entity = sensor_class.__new__(sensor_class)
    entity.coordinator = coordinator
    entity.entity_description = description
    return entity


def airflow_sensor_keys(model: str, profile: object = SAVE_PROFILE) -> tuple[str, ...]:
    """Return airflow sensor keys selected for a model."""
    implementation = getattr(sensor_module, "airflow_sensor_descriptions", None)
    if implementation is None:
        return ()
    return tuple(desc.key for desc in implementation(model, profile))


def calibration_suggestions(model: str, profile: object = SAVE_PROFILE, options: dict[str, float] | None = None) -> dict[str, float]:
    """Return production calibration suggestions when available."""
    implementation = getattr(config_flow_module, "_airflow_calibration_suggestions", None)
    if implementation is None:
        return {}
    return implementation(model, profile, options or {})


def reset_calibration(user_input: dict[str, object], current_model: str) -> dict[str, object]:
    """Run production model-change calibration cleanup when available."""
    implementation = getattr(config_flow_module, "_reset_airflow_calibration_on_model_change", None)
    if implementation is None:
        return dict(user_input)
    return implementation(user_input, current_model)


class AirflowCalculationTest(unittest.TestCase):
    """Airflow uses the model maximum and actual fan output percentage."""

    def test_airflow_scales_linearly_from_actual_fan_output(self) -> None:
        """A partial fan output returns the matching share of maximum airflow."""
        self.assertEqual(calculate_airflow(VSR500_MAX_AIRFLOW, 46), VSR500_SUPPLY_AIRFLOW_AT_46_PERCENT)

    def test_airflow_clamps_fan_output_to_valid_percentage(self) -> None:
        """Invalid output values cannot produce negative or above-maximum airflow."""
        self.assertEqual(calculate_airflow(VSR500_MAX_AIRFLOW, -5), 0)
        self.assertEqual(calculate_airflow(VSR500_MAX_AIRFLOW, 120), VSR500_MAX_AIRFLOW)

    def test_airflow_is_unknown_without_reference_or_output(self) -> None:
        """Missing model airflow or live output keeps the estimate unavailable."""
        self.assertIsNone(calculate_airflow(None, 50))
        self.assertIsNone(calculate_airflow(VSR500_MAX_AIRFLOW, None))


class AirflowSensorTest(unittest.TestCase):
    """Calculated sensors expose whole-unit supply and extract airflow."""

    def test_supply_and_extract_use_their_own_live_outputs(self) -> None:
        """Different SAF and EAF percentages produce different airflow values."""
        coordinator = FakeCoordinator("VSR 500", saf_pct=46, eaf_pct=44)

        self.assertEqual(airflow_sensor("supply_airflow", coordinator).native_value, VSR500_SUPPLY_AIRFLOW_AT_46_PERCENT)
        self.assertEqual(airflow_sensor("extract_airflow", coordinator).native_value, VSR500_EXTRACT_AIRFLOW_AT_44_PERCENT)

    def test_calibrated_maximum_overrides_passport_per_fan_side(self) -> None:
        """Supply and extract calibration values are applied independently."""
        coordinator = FakeCoordinator(
            "VSR 500",
            saf_pct=46,
            eaf_pct=44,
            options={"supply_airflow_max": 700, "extract_airflow_max": 500},
        )

        self.assertEqual(airflow_sensor("supply_airflow", coordinator).native_value, CALIBRATED_SUPPLY_AIRFLOW_AT_46_PERCENT)
        self.assertEqual(airflow_sensor("extract_airflow", coordinator).native_value, CALIBRATED_EXTRACT_AIRFLOW_AT_44_PERCENT)

    def test_d24810_uses_legacy_pwm_output_registers(self) -> None:
        """Legacy models calculate airflow from profile-owned PWM outputs."""
        coordinator = FakeCoordinator("VSR500", saf_pct=46, eaf_pct=44, profile=D24810_PROFILE)

        self.assertEqual(airflow_sensor("supply_airflow", coordinator).native_value, VSR500_SUPPLY_AIRFLOW_AT_46_PERCENT)
        self.assertEqual(airflow_sensor("extract_airflow", coordinator).native_value, VSR500_EXTRACT_AIRFLOW_AT_44_PERCENT)

    def test_missing_live_output_keeps_sensor_unknown(self) -> None:
        """Unavailable fan output does not become a false zero airflow."""
        coordinator = FakeCoordinator("VSR 500", saf_pct=None, eaf_pct=44)

        self.assertIsNone(airflow_sensor("supply_airflow", coordinator).native_value)

    def test_attributes_explain_passport_and_calibrated_references(self) -> None:
        """Sensor attributes expose the percentage, reference, and its source."""
        coordinator = FakeCoordinator("VSR 500", saf_pct=46, eaf_pct=44, options={"supply_airflow_max": 700})

        self.assertDictEqual(
            airflow_sensor("supply_airflow", coordinator).extra_state_attributes,
            {
                "fan_output_percentage": 46.0,
                "reference_max_airflow_m3h": 700.0,
                "reference_source": "calibrated",
            },
        )
        self.assertDictEqual(
            airflow_sensor("extract_airflow", coordinator).extra_state_attributes,
            {
                "fan_output_percentage": 44.0,
                "reference_max_airflow_m3h": 609.0,
                "reference_source": "passport",
            },
        )

    def test_sensor_creation_matches_model_fans_and_known_airflow(self) -> None:
        """Only supported fan sides with a known maximum create entities."""
        self.assertEqual(airflow_sensor_keys("VSR 500"), ("supply_airflow", "extract_airflow"))
        self.assertEqual(airflow_sensor_keys("VSC 100"), ("supply_airflow", "extract_airflow"))
        self.assertEqual(airflow_sensor_keys("VR 400 DC"), ())
        self.assertEqual(airflow_sensor_keys("VSR500", D24810_PROFILE), ("supply_airflow", "extract_airflow"))


class AirflowCalibrationOptionsTest(unittest.TestCase):
    """Options Flow exposes safe per-side airflow calibration values."""

    def test_passport_values_are_suggested_for_supported_fan_sides(self) -> None:
        """Two-fan and single-fan units receive the appropriate defaults."""
        self.assertDictEqual(
            calibration_suggestions("VSR 500"),
            {
                "supply_airflow_max": 609.0,
                "extract_airflow_max": 609.0,
            },
        )
        self.assertDictEqual(
            calibration_suggestions("VSC 100"),
            {
                "supply_airflow_max": 166.0,
                "extract_airflow_max": 166.0,
            },
        )

    def test_saved_calibration_replaces_passport_suggestions(self) -> None:
        """Existing per-side calibration remains visible when editing options."""
        self.assertDictEqual(
            calibration_suggestions(
                "VSR 500",
                options={"supply_airflow_max": 700, "extract_airflow_max": 500},
            ),
            {"supply_airflow_max": 700.0, "extract_airflow_max": 500.0},
        )

    def test_unknown_passport_airflow_has_no_calibration_fields(self) -> None:
        """A model without qv max cannot accept a misleading calibration."""
        self.assertDictEqual(calibration_suggestions("VR 400 DC"), {})

    def test_model_change_clears_previous_calibration(self) -> None:
        """Calibration belonging to another model is removed on submission."""
        submitted = {
            "model": "VSR 700",
            "supply_airflow_max": 700,
            "extract_airflow_max": 500,
            "update_interval": 60,
        }

        self.assertDictEqual(reset_calibration(submitted, "VSR 500"), {"model": "VSR 700", "update_interval": 60})

    def test_same_model_preserves_calibration(self) -> None:
        """Editing other options does not discard valid calibration."""
        submitted = {"model": "VSR 500", "supply_airflow_max": 700, "extract_airflow_max": 500}

        self.assertDictEqual(reset_calibration(submitted, "VSR 500"), submitted)

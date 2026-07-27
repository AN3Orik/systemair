"""Tests for model specification lookup, including device-reported model names."""

# ruff: noqa: S101

from __future__ import annotations

import unittest

from custom_components.systemair.const import MODEL_SPECS, normalise_model_name, resolve_model_specs

VTR_300_MAX_AIRFLOW = 351
VTR_500_MAX_AIRFLOW = 572


class TestResolveModelSpecs(unittest.TestCase):
    """Model specs must resolve from catalogue keys and from what units actually report."""

    def test_device_reported_name_resolves(self) -> None:
        """A unit reporting "SAVE VTR 300 R" must resolve to the VTR 300/B R specs."""
        specs = resolve_model_specs("SAVE VTR 300 R", {})
        assert specs is not None
        assert specs["max_airflow_m3h"] == VTR_300_MAX_AIRFLOW

    def test_device_reported_name_resolves_for_both_handings(self) -> None:
        """Handing must not affect resolution."""
        for model in ("SAVE VTR 300 L", "SAVE VTR 300 R"):
            assert resolve_model_specs(model, {}) is not None, model

    def test_exact_catalogue_key_still_resolves(self) -> None:
        """The existing exact lookup must be unchanged."""
        assert resolve_model_specs("VTR 300/B R", {})["max_airflow_m3h"] == VTR_300_MAX_AIRFLOW

    def test_default_model_still_resolves(self) -> None:
        """The fallback model used when none is configured must keep working."""
        assert resolve_model_specs("VSR 300", {}) is not None

    def test_alias_is_honoured(self) -> None:
        """A device-profile alias must resolve a name that matches nothing else."""
        specs = resolve_model_specs("WHATEVER", {"WHATEVER": "VTR 300/B R"})
        assert specs["max_airflow_m3h"] == VTR_300_MAX_AIRFLOW

    def test_alias_takes_precedence_over_normalisation(self) -> None:
        """
        An alias must be consulted before the normalised fallback, not merely fill a gap.

        "SAVE VTR 300 R" resolves to the VTR 300 specs on its own, so aliasing it to a
        different unit proves the alias wins: normalising first would yield VTR 300.
        """
        specs = resolve_model_specs("SAVE VTR 300 R", {"SAVE VTR 300 R": "VTR 500 R"})
        assert specs["max_airflow_m3h"] == VTR_500_MAX_AIRFLOW

    def test_unknown_model_returns_none(self) -> None:
        """An unrecognised model must still return None rather than a wrong match."""
        assert resolve_model_specs("Not A Real Unit 999", {}) is None

    def test_normalisation_is_unambiguous(self) -> None:
        """No two catalogue models may normalise to the same key."""
        normalised = [normalise_model_name(key) for key in MODEL_SPECS]
        assert len(normalised) == len(set(normalised))


if __name__ == "__main__":
    unittest.main()

"""Tests for fail-safe profile auto-detection."""

from __future__ import annotations

import unittest

from custom_components.systemair.profiles import DEVICE_PROFILE_LEGACY_D24810, DEVICE_PROFILE_SAVE
from custom_components.systemair.profiles.detection import DetectionOutcome, ProfileDetectionError, detect_profile_from_probe_values

EXPECTED_D24810_SCORE = 6
EXPECTED_SAVE_SCORE = 4


class ProfileDetectionTest(unittest.TestCase):
    """Auto-detection must never guess ambiguous profile matches."""

    def test_detects_d24810_when_only_d24810_probe_matches(self) -> None:
        """D24810 wins only when D24810 probes are valid and SAVE probes are invalid."""
        outcome = detect_profile_from_probe_values(
            save_values={1131: 99, 1161: 99, 1274: 99, 2001: 9999},
            d24810_values={101: 1, 108: 1, 501: 0, 601: 12, 602: 30},
        )

        assert outcome.profile_id == DEVICE_PROFILE_LEGACY_D24810  # noqa: S101
        assert outcome.d24810_score == EXPECTED_D24810_SCORE  # noqa: S101
        assert outcome.save_score == 0  # noqa: S101

    def test_detects_save_when_only_save_probe_matches(self) -> None:
        """SAVE wins only when SAVE probes are valid and D24810 probes are invalid."""
        outcome = detect_profile_from_probe_values(
            save_values={1131: 3, 1161: 1, 1274: 0, 2001: 210},
            d24810_values={101: 99, 108: 99, 501: 99, 601: 0, 602: 70000},
        )

        assert outcome.profile_id == DEVICE_PROFILE_SAVE  # noqa: S101
        assert outcome.save_score == EXPECTED_SAVE_SCORE  # noqa: S101
        assert outcome.d24810_score == 0  # noqa: S101

    def test_requires_manual_selection_when_both_profiles_match(self) -> None:
        """Ambiguous valid probes must force manual selection."""
        try:
            detect_profile_from_probe_values(
                save_values={1131: 3, 1161: 1, 1274: 0, 2001: 210},
                d24810_values={101: 1, 108: 1, 501: 0, 601: 12, 602: 30},
            )
        except ProfileDetectionError:
            return
        self.fail("ProfileDetectionError was not raised")

    def test_requires_manual_selection_when_no_profile_matches(self) -> None:
        """Invalid probes for both profiles must force manual selection."""
        try:
            detect_profile_from_probe_values(
                save_values={1131: 99, 1161: 99, 1274: 99, 2001: 9999},
                d24810_values={101: 99, 108: 99, 501: 99, 601: 0, 602: 70000},
            )
        except ProfileDetectionError:
            return
        self.fail("ProfileDetectionError was not raised")

    def test_d24810_requires_valid_system_type_probe(self) -> None:
        """Generic D24810-looking values are not enough without REG_SYSTEM_TYPE."""
        try:
            detect_profile_from_probe_values(
                save_values={1131: 99, 1161: 99, 1274: 99, 2001: 9999},
                d24810_values={101: 1, 108: 1, 501: 99, 601: 12, 602: 30},
            )
        except ProfileDetectionError:
            return
        self.fail("ProfileDetectionError was not raised")

    def test_outcome_records_scores(self) -> None:
        """Detection outcome exposes the scores used for diagnostics."""
        outcome = DetectionOutcome(profile_id=DEVICE_PROFILE_SAVE, save_score=EXPECTED_SAVE_SCORE, d24810_score=0)

        assert outcome.profile_id == DEVICE_PROFILE_SAVE  # noqa: S101
        assert outcome.save_score == EXPECTED_SAVE_SCORE  # noqa: S101
        assert outcome.d24810_score == 0  # noqa: S101

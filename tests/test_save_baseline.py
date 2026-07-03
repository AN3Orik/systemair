"""Regression tests for the current SAVE Modbus baseline."""

from __future__ import annotations

import unittest

from custom_components.systemair.api import READ_BLOCKS_ALARM_DETAILS, READ_BLOCKS_ALARM_HISTORY, READ_BLOCKS_BASE
from custom_components.systemair.modbus import parameter_map

EXPECTED_SAVE_READ_BLOCKS_BASE = [
    (1001, 62),
    (1101, 88),
    (1201, 74),
    (1351, 3),
    (1410, 10),
    (2001, 125),
    (2126, 24),
    (2201, 63),
    (2311, 8),
    (2401, 53),
    (2504, 18),
    (3002, 116),
    (4001, 12),
    (4101, 20),
    (7001, 6),
    (12011, 2),
    (12101, 41),
    (12301, 17),
    (12401, 5),
    (12544, 1),
    (14001, 4),
    (14101, 5),
    (14201, 4),
    (14301, 11),
    (14381, 1),
    (15901, 10),
]


class SaveBaselineTest(unittest.TestCase):
    """Protect the current SAVE register map before profile refactoring."""

    def test_save_read_blocks_are_unchanged(self) -> None:
        """The SAVE polling blocks must stay stable during profile refactoring."""
        assert READ_BLOCKS_BASE == EXPECTED_SAVE_READ_BLOCKS_BASE  # noqa: S101
        assert READ_BLOCKS_ALARM_DETAILS == [(15016, 125), (15141, 125), (15266, 125), (15391, 125), (15516, 125)]  # noqa: S101
        assert READ_BLOCKS_ALARM_HISTORY == [(15641, 125), (15766, 125), (15891, 10)]  # noqa: S101

    def test_save_key_registers_are_unchanged(self) -> None:
        """The SAVE entity-critical register addresses must stay stable."""
        expected = {
            "REG_USERMODE_MANUAL_AIRFLOW_LEVEL_SAF": 1131,
            "REG_USERMODE_MODE": 1161,
            "REG_FAN_REGULATION_UNIT": 1274,
            "REG_TC_SP": 2001,
            "REG_FILTER_REPLACEMENT_TIME_L": 7002,
            "REG_SENSOR_RPM_SAF": 12401,
            "REG_SENSOR_RPM_EAF": 12402,
            "REG_OUTPUT_SAF": 14001,
            "REG_OUTPUT_EAF": 14002,
        }

        for key, register in expected.items():
            with self.subTest(key=key):
                assert parameter_map[key].register == register  # noqa: S101

"""Business tests for HomeSolution alarm history."""

# ruff: noqa: S101, SLF001

from __future__ import annotations

import unittest
from types import SimpleNamespace

from custom_components.systemair.coordinator import SystemairDataUpdateCoordinator
from custom_components.systemair.sensor import SystemairSensor
from custom_components.systemair.systemair_api.models.ventilation_unit import VentilationUnit


class HomeSolutionAlarmHistoryTest(unittest.TestCase):
    """Cloud alarm-log registers use the common SAVE history representation."""

    def test_cloud_alarm_log_builds_state_and_attributes(self) -> None:
        """Zero-based cloud IDs are read through one-based SAVE log addresses."""
        unit = VentilationUnit("device", "Unit")
        unit.registers.update(
            {
                637: 1,
                638: 1,
                640: 2026,
                641: 7,
                642: 18,
                643: 12,
                644: 34,
                645: 56,
            }
        )
        unit.update_modbus_register_map(
            {
                15700: 637,
                15701: 638,
                15703: 640,
                15704: 641,
                15705: 642,
                15706: 643,
                15707: 644,
                15708: 645,
            }
        )
        coordinator = SystemairDataUpdateCoordinator.__new__(SystemairDataUpdateCoordinator)
        coordinator._is_homesolution = True
        coordinator.data = unit
        coordinator.config_entry = SimpleNamespace(options={"enable_alarm_history": True})

        sensor = SystemairSensor.__new__(SystemairSensor)
        sensor.coordinator = coordinator
        sensor._is_homesolution = True
        sensor.entity_description = SimpleNamespace(key="alarm_history")

        assert sensor._get_alarm_history_state() == "Frost protection temperature sensor"
        assert sensor.extra_state_attributes == {
            "history": [
                {
                    "alarm": "Frost protection temperature sensor",
                    "status": "Active",
                    "timestamp": "2026-07-18 12:34:56",
                }
            ]
        }


if __name__ == "__main__":
    unittest.main()

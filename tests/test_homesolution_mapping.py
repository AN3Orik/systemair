"""Business tests for HomeSolution register resolution."""

# ruff: noqa: PLR2004, S101, SLF001

from __future__ import annotations

import unittest
from types import SimpleNamespace

from custom_components.systemair import homesolution_mapping
from custom_components.systemair.coordinator import SystemairDataUpdateCoordinator
from custom_components.systemair.entity import SystemairEntity
from custom_components.systemair.modbus import parameter_map
from custom_components.systemair.systemair_api.models.ventilation_unit import VentilationUnit
from custom_components.systemair.systemair_api.utils.register_constants import RegisterConstants


class HomeSolutionMappingTest(unittest.TestCase):
    """Cloud data resolves to the same values as the SAVE Modbus profile."""

    def test_mainboard_id_wins_and_uses_modbus_scaling(self) -> None:
        """HomeSolution mainboard values take precedence over duplicate Modbus IDs."""
        resolver = getattr(homesolution_mapping, "resolve_homesolution_value", None)
        candidates = getattr(homesolution_mapping, "homesolution_register_candidates", None)
        assert resolver is not None
        assert candidates is not None
        register = parameter_map["REG_SENSOR_OAT"]
        unit = VentilationUnit("device", "Unit")
        unit.registers = {
            RegisterConstants.REG_MAINBOARD_SENSOR_OAT: 215,
            RegisterConstants.REG_SENSOR_OAT: 999,
        }

        assert candidates(register)[0] == RegisterConstants.REG_MAINBOARD_SENSOR_OAT
        assert resolver(unit, register) == 21.5

    def test_signed_values_and_output_aliases_are_decoded(self) -> None:
        """Signed temperatures and logical Y outputs share SAVE semantics."""
        resolver = getattr(homesolution_mapping, "resolve_homesolution_value", None)
        assert resolver is not None
        unit = VentilationUnit("device", "Unit")
        unit.registers = {
            RegisterConstants.REG_MAINBOARD_SENSOR_SAT: 65526,
            RegisterConstants.REG_MAINBOARD_OUTPUT_AO2: 47,
        }

        assert resolver(unit, parameter_map["REG_SENSOR_SAT"]) == -1.0
        assert resolver(unit, parameter_map["REG_OUTPUT_Y2_ANALOG"]) == 47.0

    def test_extension_modbus_mapping_resolves_cloud_specific_data_item_id(self) -> None:
        """GetView metadata bridges SAVE addresses to arbitrary cloud data-item IDs."""
        unit = VentilationUnit("device", "Unit")
        unit.registers[900] = 47
        unit.update_modbus_register_map({14000: 900})

        assert homesolution_mapping.resolve_homesolution_value(unit, parameter_map["REG_OUTPUT_SAF"]) == 47.0

    def test_missing_capability_is_none_but_summary_fallback_remains_available(self) -> None:
        """Absent hardware stays unavailable while explicit cloud summaries still work."""
        resolver = getattr(homesolution_mapping, "resolve_homesolution_value", None)
        assert resolver is not None
        unit = VentilationUnit("device", "Unit")

        assert resolver(unit, parameter_map["REG_OUTPUT_Y4_CIRC_PUMP"]) is None
        assert resolver(unit, parameter_map["REG_USERMODE_MODE"]) is None
        assert resolver(unit, parameter_map["REG_OUTPUT_SAF"]) is None
        assert resolver(unit, parameter_map["REG_FILTER_PERIOD"]) is None
        assert resolver(unit, parameter_map["REG_IAQ_LEVEL"]) is None

        unit.user_mode = 12
        assert resolver(unit, parameter_map["REG_USERMODE_MODE"]) == 12.0

    def test_cloud_fan_stop_value_matches_save_climate_semantics(self) -> None:
        """Action and readback IDs use their distinct airflow enumerations."""
        resolver = homesolution_mapping.resolve_homesolution_value
        register = parameter_map["REG_USERMODE_MANUAL_AIRFLOW_LEVEL_SAF"]
        unit = VentilationUnit("device", "Unit")
        unit.registers[RegisterConstants.REG_MAINBOARD_USERMODE_MANUAL_AIRFLOW_LEVEL_SAF] = 1

        assert resolver(unit, register) == 0.0

        unit.registers[RegisterConstants.REG_MAINBOARD_USERMODE_MANUAL_AIRFLOW_LEVEL_SAF] = 2
        assert resolver(unit, register) == 2.0

        unit.registers.clear()
        unit.registers[RegisterConstants.REG_MAINBOARD_SPEED_INDICATION_APP] = 1
        assert resolver(unit, register) == 2.0

        unit.registers[RegisterConstants.REG_MAINBOARD_SPEED_INDICATION_APP] = 0
        assert resolver(unit, register) == 0.0

    def test_write_candidates_use_visible_home_controls_and_translate_values(self) -> None:
        """Cloud actions are enabled by their visible writable readback controls."""
        candidates = homesolution_mapping.homesolution_write_candidates
        capability = homesolution_mapping.homesolution_write_capability_id
        encode = homesolution_mapping.encode_homesolution_write_value
        mode = parameter_map["REG_USERMODE_HMI_CHANGE_REQUEST"]
        fan = parameter_map["REG_USERMODE_MANUAL_AIRFLOW_LEVEL_SAF"]
        filter_period = parameter_map["REG_FILTER_PERIOD"]
        eco = parameter_map["REG_ECO_MODE_ON_OFF"]

        assert candidates(mode)[0] == RegisterConstants.REG_MAINBOARD_USERMODE_HMI_CHANGE_REQUEST
        assert candidates(fan)[0] == RegisterConstants.REG_MAINBOARD_USERMODE_MANUAL_AIRFLOW_LEVEL_SAF
        assert candidates(filter_period)[0] == RegisterConstants.REG_MAINBOARD_FILTER_PERIOD_SET
        assert (
            capability(mode, RegisterConstants.REG_MAINBOARD_USERMODE_HMI_CHANGE_REQUEST)
            == RegisterConstants.REG_MAINBOARD_USERMODE_MODE_HMI
        )
        assert (
            capability(fan, RegisterConstants.REG_MAINBOARD_USERMODE_MANUAL_AIRFLOW_LEVEL_SAF)
            == RegisterConstants.REG_MAINBOARD_SPEED_INDICATION_APP
        )
        assert encode(mode, 4) == 4
        assert encode(fan, 0) == 1
        assert encode(fan, 3) == 3
        assert encode(eco, 1) == "true"
        assert encode(eco, 0) == "false"

    def test_coordinator_uses_capabilities_and_entity_becomes_unavailable(self) -> None:
        """Entity availability follows the resolved HomeSolution register."""
        unit = VentilationUnit("device", "Unit")
        unit.registers[RegisterConstants.REG_MAINBOARD_OUTPUT_AO2] = 47
        coordinator = SystemairDataUpdateCoordinator.__new__(SystemairDataUpdateCoordinator)
        coordinator._is_webapi = False
        coordinator._is_homesolution = True
        coordinator.data = unit

        assert coordinator.get_modbus_data(parameter_map["REG_OUTPUT_Y2_ANALOG"]) == 47.0
        assert coordinator.has_modbus_data(parameter_map["REG_OUTPUT_Y2_ANALOG"]) is True
        assert coordinator.has_modbus_data(parameter_map["REG_OUTPUT_Y4_CIRC_PUMP"]) is False

        entity = SystemairEntity.__new__(SystemairEntity)
        entity.coordinator = SimpleNamespace(
            data=unit,
            client=SimpleNamespace(available=True),
            has_modbus_data=lambda register: register.short == "REG_OUTPUT_Y2_ANALOG",
        )
        entity._is_homesolution = True
        entity.entity_description = SimpleNamespace(registry=parameter_map["REG_OUTPUT_Y4_CIRC_PUMP"])

        assert entity.available is False


if __name__ == "__main__":
    unittest.main()

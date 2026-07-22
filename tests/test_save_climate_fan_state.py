"""Business regressions for SAVE climate fan-state readback."""

# ruff: noqa: S101, SLF001

from __future__ import annotations

import unittest
from types import SimpleNamespace
from typing import Any

from homeassistant.components.climate import HVACMode
from homeassistant.components.climate.const import FAN_LOW, FAN_MEDIUM, FAN_OFF

from custom_components.systemair.climate import SystemairClimateEntity
from custom_components.systemair.const import API_TYPE_HOMESOLUTION, PRESET_MODE_AUTO
from custom_components.systemair.coordinator import SystemairDataUpdateCoordinator
from custom_components.systemair.modbus import parameter_map
from custom_components.systemair.profiles.save import SAVE_PROFILE


class FakeCoordinator:
    """Expose SAVE values to the real climate entity without transport I/O."""

    def __init__(
        self,
        values: dict[str, float | bool | None],
        *,
        homesolution: bool = False,
        writable: set[str] | None = None,
    ) -> None:
        """Initialize a complete coordinator contract used by Climate."""
        runtime_data = SimpleNamespace(
            model="VSR 500",
            mb_model=None,
            mb_hw_version=None,
            mb_sw_version=None,
            serial_number=None,
            configuration_url=None,
            profile=SAVE_PROFILE,
        )
        data = {"api_type": API_TYPE_HOMESOLUTION} if homesolution else {}
        self.config_entry = SimpleNamespace(entry_id="entry", domain="systemair", data=data, runtime_data=runtime_data)
        self.data: object = object()
        self.last_update_success = True
        self.client = SimpleNamespace(available=True)
        self.values = values
        self.writable = writable or set()
        self.writes: list[tuple[str, int]] = []
        self.refreshes = 0

    def async_add_listener(self, *_args: object, **_kwargs: object) -> Any:
        """Return a coordinator listener unsubscribe callback."""
        return lambda: None

    def get_modbus_data(self, register: object) -> float | bool | None:
        """Return a value by SAVE semantic register name."""
        return self.values.get(register.short)

    def has_modbus_data(self, register: object) -> bool:
        """Report only values supplied by the transport fixture."""
        return self.values.get(register.short) is not None

    def can_set_modbus_data(self, register: object) -> bool:
        """Report explicitly writable cloud controls."""
        return register.short in self.writable

    async def set_modbus_data(self, register: object, value: int) -> None:
        """Record the requested command at the transport boundary."""
        self.writes.append((register.short, value))

    async def async_refresh_after_write(self) -> None:
        """Record publication of post-write readback."""
        self.refreshes += 1


def climate_entity(
    *,
    homesolution: bool = False,
    writable: set[str] | None = None,
    **values: float | None,
) -> tuple[SystemairClimateEntity, FakeCoordinator]:
    """Create a real SAVE climate entity with selected live inputs."""
    coordinator = FakeCoordinator(
        {
            "REG_SPEED_INDICATION_APP": values.get("actual"),
            "REG_USERMODE_MANUAL_AIRFLOW_LEVEL_SAF": values.get("manual"),
            "REG_USERMODE_MODE": values.get("user_mode"),
            "REG_OUTPUT_SAF": values.get("saf_output"),
            "REG_OUTPUT_EAF": values.get("eaf_output"),
            "REG_FUNCTION_ACTIVE_HEATER": 0,
            "REG_FUNCTION_ACTIVE_COOLER": 0,
            "REG_TC_SP": 20,
        },
        homesolution=homesolution,
        writable=writable,
    )
    return SystemairClimateEntity(coordinator), coordinator


class SaveClimateFanStateTest(unittest.IsolatedAsyncioTestCase):
    """Climate reports actual fan state without confusing it with commands."""

    def test_auto_manual_off_command_does_not_hide_running_minimum_airflow(self) -> None:
        """An Auto-mode setpoint of zero cannot override live fan outputs/readback."""
        entity, _coordinator = climate_entity(actual=1, manual=0, user_mode=0, saf_output=35, eaf_output=31)

        assert entity.hvac_mode == HVACMode.FAN_ONLY
        assert entity.fan_mode == FAN_LOW

    def test_running_outputs_do_not_change_actual_off_fan_mode(self) -> None:
        """Outputs govern HVAC running while actual level zero remains fan mode Off."""
        entity, _coordinator = climate_entity(actual=0, manual=4, user_mode=0, saf_output=35, eaf_output=31)

        assert entity.hvac_mode == HVACMode.FAN_ONLY
        assert entity.fan_mode == FAN_OFF

    def test_stopped_schedule_wins_over_nonzero_indicated_level(self) -> None:
        """Both stopped fan outputs make the unit Off even if indication remains Minimum."""
        entity, _coordinator = climate_entity(actual=1, manual=3, user_mode=0, saf_output=0, eaf_output=0)

        assert entity.hvac_mode == HVACMode.OFF
        assert entity.fan_mode == FAN_OFF

    def test_missing_actual_level_falls_back_to_manual_setpoint_only_in_manual_mode(self) -> None:
        """Manual mode can use its own command when no actual readback exists."""
        entity, _coordinator = climate_entity(actual=None, manual=3, user_mode=1, saf_output=None, eaf_output=None)

        assert entity.hvac_mode == HVACMode.FAN_ONLY
        assert entity.fan_mode == FAN_MEDIUM

    def test_real_coordinator_preserves_missing_readback_for_manual_fallback(self) -> None:
        """Local transport absence reaches Climate as unknown instead of invented Off values."""
        coordinator = SystemairDataUpdateCoordinator.__new__(SystemairDataUpdateCoordinator)
        coordinator._is_webapi = False
        coordinator._is_homesolution = False
        coordinator.data = {
            str(parameter_map["REG_USERMODE_MODE"].register - 1): 1,
            str(parameter_map["REG_USERMODE_MANUAL_AIRFLOW_LEVEL_SAF"].register - 1): 3,
        }
        entity = SystemairClimateEntity.__new__(SystemairClimateEntity)
        entity.coordinator = coordinator
        entity._is_homesolution = False

        assert entity.hvac_mode == HVACMode.FAN_ONLY
        assert entity.fan_mode == FAN_MEDIUM

    def test_missing_actual_level_does_not_expose_auto_setpoint_as_fan_mode(self) -> None:
        """Auto mode keeps an unknown actual discrete level unknown while fans run."""
        entity, _coordinator = climate_entity(actual=None, manual=4, user_mode=0, saf_output=35, eaf_output=31)

        assert entity.hvac_mode == HVACMode.FAN_ONLY
        assert entity.fan_mode is None

    def test_non_discrete_and_invalid_indications_are_not_reported_as_fan_modes(self) -> None:
        """Automatic, fractional, and non-finite indications cannot invent a writable mode."""
        for actual in (6, 7, 1.5, float("nan"), float("inf")):
            with self.subTest(actual=actual):
                entity, _coordinator = climate_entity(actual=actual, manual=4, user_mode=0, saf_output=35, eaf_output=31)

                try:
                    hvac_mode = entity.hvac_mode
                    fan_mode = entity.fan_mode
                except (OverflowError, ValueError) as exc:
                    self.fail(f"Invalid actual level raised {exc!r}")
                assert hvac_mode == HVACMode.FAN_ONLY
                assert fan_mode is None

    def test_homesolution_realtime_airflow_wins_over_stale_stopped_outputs(self) -> None:
        """A fresh cloud status cannot be overridden by outputs from an older poll."""
        entity, _coordinator = climate_entity(
            actual=2,
            manual=0,
            user_mode=0,
            saf_output=0,
            eaf_output=0,
            homesolution=True,
        )

        assert entity.hvac_mode == HVACMode.FAN_ONLY
        assert entity.fan_mode == FAN_LOW

    def test_homesolution_availability_accepts_websocket_actual_readback(self) -> None:
        """Cloud Climate stays available when status supplies actual airflow without command readback."""
        writable = {
            "REG_USERMODE_HMI_CHANGE_REQUEST",
            "REG_USERMODE_MANUAL_AIRFLOW_LEVEL_SAF",
            "REG_TC_SP",
        }
        entity, _coordinator = climate_entity(
            actual=2,
            manual=None,
            user_mode=0,
            saf_output=None,
            eaf_output=None,
            homesolution=True,
            writable=writable,
        )

        assert entity.available is True

    def test_homesolution_availability_accepts_manual_readback_fallback(self) -> None:
        """Cloud Climate remains available in Manual mode without actual readback."""
        writable = {
            "REG_USERMODE_HMI_CHANGE_REQUEST",
            "REG_USERMODE_MANUAL_AIRFLOW_LEVEL_SAF",
            "REG_TC_SP",
        }
        entity, _coordinator = climate_entity(
            actual=None,
            manual=3,
            user_mode=1,
            saf_output=None,
            eaf_output=None,
            homesolution=True,
            writable=writable,
        )

        assert entity.available is True
        assert entity.fan_mode == FAN_MEDIUM

    async def test_preset_write_always_publishes_refreshed_readback(self) -> None:
        """Preset commands follow the same post-write refresh contract as other controls."""
        entity, coordinator = climate_entity(actual=2, manual=2, user_mode=1, saf_output=35, eaf_output=31)

        await entity.async_set_preset_mode(PRESET_MODE_AUTO)

        assert coordinator.writes == [("REG_USERMODE_HMI_CHANGE_REQUEST", 1)]
        assert coordinator.refreshes == 1


if __name__ == "__main__":
    unittest.main()

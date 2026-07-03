"""Tests for D24810 climate mapping safety."""

from __future__ import annotations

import unittest
from types import SimpleNamespace

from homeassistant.components.climate import ClimateEntityFeature, HVACMode
from homeassistant.components.climate.const import FAN_MEDIUM

from custom_components.systemair.climate import SystemairD24810ClimateEntity
from custom_components.systemair.profiles.d24810 import D24810_PROFILE, d24810_parameter_map


class D24810ClimateMappingTest(unittest.IsolatedAsyncioTestCase):
    """D24810 climate must use D24810 registers only."""

    def test_climate_mapping_registers_exist_in_d24810_registry(self) -> None:
        """Climate mapping points at existing D24810 register keys."""
        required = D24810_PROFILE.climate_registers

        assert "fan_mode" in required  # noqa: S101
        assert "current_temperature" in required  # noqa: S101
        assert "target_temperature" in required  # noqa: S101
        assert required["fan_mode"] in d24810_parameter_map  # noqa: S101
        assert required["current_temperature"] in d24810_parameter_map  # noqa: S101
        assert required["target_temperature"] in d24810_parameter_map  # noqa: S101

    def test_climate_mapping_does_not_use_save_register_names(self) -> None:
        """D24810 climate mapping never reuses SAVE-only climate registers."""
        save_only_names = {"REG_TC_SP", "REG_USERMODE_MODE", "REG_OUTPUT_SAF", "REG_OUTPUT_EAF"}

        assert save_only_names.isdisjoint(set(D24810_PROFILE.climate_registers.values()))  # noqa: S101

    def test_d24810_climate_entity_is_fan_mode_only(self) -> None:
        """D24810 climate does not expose unsupported temperature writes."""
        runtime_data = SimpleNamespace(
            model="VR400",
            mb_model=None,
            mb_hw_version=None,
            mb_sw_version=None,
            serial_number=None,
            configuration_url=None,
            profile=D24810_PROFILE,
        )
        config_entry = SimpleNamespace(entry_id="entry", domain="systemair", data={}, runtime_data=runtime_data)

        class FakeCoordinator:
            def __init__(self) -> None:
                self.config_entry = config_entry
                self.data = {}
                self.last_update_success = True

            def async_add_listener(self, *_args: object, **_kwargs: object) -> object:
                return lambda: None

            def get_modbus_data(self, _register: object) -> None:
                return None

        entity = SystemairD24810ClimateEntity(FakeCoordinator())

        assert entity.supported_features == ClimateEntityFeature.FAN_MODE  # noqa: S101

    async def test_set_hvac_mode_fan_only_preserves_active_fan_speed(self) -> None:
        """Setting fan-only does not downgrade an already running D24810 unit."""
        fan_register = d24810_parameter_map[D24810_PROFILE.climate_registers["fan_mode"]]
        runtime_data = SimpleNamespace(
            model="VR400",
            mb_model=None,
            mb_hw_version=None,
            mb_sw_version=None,
            serial_number=None,
            configuration_url=None,
            profile=D24810_PROFILE,
        )
        config_entry = SimpleNamespace(entry_id="entry", domain="systemair", data={}, runtime_data=runtime_data)

        class FakeCoordinator:
            def __init__(self) -> None:
                self.config_entry = config_entry
                self.data = {}
                self.last_update_success = True
                self.writes: list[tuple[str, int]] = []

            def async_add_listener(self, *_args: object, **_kwargs: object) -> object:
                return lambda: None

            def get_modbus_data(self, register: object) -> int | None:
                if register == fan_register:
                    return 2
                return None

            async def set_modbus_data(self, register: object, value: int) -> None:
                self.writes.append((register.short, value))

            async def async_refresh(self) -> None:
                return None

        coordinator = FakeCoordinator()
        entity = SystemairD24810ClimateEntity(coordinator)

        assert entity.fan_mode == FAN_MEDIUM  # noqa: S101

        await entity.async_set_hvac_mode(HVACMode.FAN_ONLY)

        assert coordinator.writes == []  # noqa: S101

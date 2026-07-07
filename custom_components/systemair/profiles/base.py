"""Device profile primitives for Systemair integrations."""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Mapping

    from homeassistant.const import Platform

    from custom_components.systemair.modbus import ModbusParameter

type ReadBlock = tuple[int, int]


@dataclass(frozen=True)
class ProfilePowerRegisters:
    """Profile register keys used by calculated power sensors."""

    supply_output: str
    extract_output: str
    heater_output: str | None = None
    heater_output_is_percentage: bool = False


@dataclass(frozen=True)
class ProfileEntityDescriptions:
    """Profile-owned entity metadata grouped by Home Assistant platform."""

    sensors: tuple[Any, ...] = ()
    binary_sensors: tuple[Any, ...] = ()
    switches: tuple[Any, ...] = ()
    selects: tuple[Any, ...] = ()
    numbers: tuple[Any, ...] = ()
    buttons: tuple[Any, ...] = ()


@dataclass(frozen=True)
class DeviceProfile:
    """Runtime profile for a specific Systemair Modbus register map."""

    profile_id: str
    name: str
    supported_api_types: tuple[str, ...]
    supported_platforms: tuple[Platform, ...]
    registry: Mapping[str, ModbusParameter]
    read_blocks: tuple[ReadBlock, ...]
    test_register: int
    model_options: tuple[str, ...] = ()
    model_aliases: Mapping[str, str] = field(default_factory=dict)
    alarm_detail_blocks: tuple[ReadBlock, ...] = ()
    alarm_history_blocks: tuple[ReadBlock, ...] = ()
    entities: ProfileEntityDescriptions = field(default_factory=ProfileEntityDescriptions)
    climate_registers: Mapping[str, str] = field(default_factory=dict)
    power_registers: ProfilePowerRegisters | None = None

    def __post_init__(self) -> None:
        """Freeze mutable mappings passed by profile modules."""
        object.__setattr__(self, "registry", MappingProxyType(dict(self.registry)))
        object.__setattr__(self, "model_aliases", MappingProxyType(dict(self.model_aliases)))
        object.__setattr__(self, "climate_registers", MappingProxyType(dict(self.climate_registers)))

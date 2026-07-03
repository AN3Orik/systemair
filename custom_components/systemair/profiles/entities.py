"""Profile-level entity description primitives."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Protocol

from custom_components.systemair.const import LOGGER

if TYPE_CHECKING:
    from custom_components.systemair.modbus import ModbusParameter
    from custom_components.systemair.profiles.base import DeviceProfile


class ProfileEntityRef(Protocol):
    """Common profile entity fields needed for register resolution."""

    key: str
    register_key: str


@dataclass(frozen=True)
class SensorProfileEntity:
    """Sensor metadata owned by a device profile."""

    key: str
    register_key: str
    translation_key: str | None = None
    device_class: Any | None = None
    state_class: Any | None = None
    native_unit_of_measurement: str | None = None
    entity_category: Any | None = None
    icon: str | None = None


@dataclass(frozen=True)
class BinarySensorProfileEntity:
    """Binary sensor metadata owned by a device profile."""

    key: str
    register_key: str
    translation_key: str | None = None
    device_class: Any | None = None
    entity_category: Any | None = None


@dataclass(frozen=True)
class SwitchProfileEntity:
    """Switch metadata owned by a device profile."""

    key: str
    register_key: str
    translation_key: str | None = None
    icon: str | None = None
    entity_category: Any | None = None


@dataclass(frozen=True)
class SelectProfileEntity:
    """Select metadata owned by a device profile."""

    key: str
    register_key: str
    options_map: dict[int, str]
    translation_key: str | None = None
    icon: str | None = None
    entity_category: Any | None = None


@dataclass(frozen=True)
class NumberProfileEntity:
    """Number metadata owned by a device profile."""

    key: str
    register_key: str
    translation_key: str | None = None
    native_unit_of_measurement: str | None = None
    entity_category: Any | None = None
    mode: str | None = None


def resolve_profile_entity_register(profile: DeviceProfile, desc: ProfileEntityRef, platform: str) -> ModbusParameter | None:
    """Return a profile entity register, or skip stale metadata safely."""
    register = profile.registry.get(desc.register_key)
    if register is None:
        LOGGER.warning(
            "Skipping %s entity %s for profile %s: register key %s is not defined",
            platform,
            desc.key,
            profile.profile_id,
            desc.register_key,
        )
    return register

"""Profile-level entity description primitives."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


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

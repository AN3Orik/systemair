"""Resolve actual SAVE fan state independently from fan commands."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Any

from homeassistant.components.climate.const import FAN_HIGH, FAN_LOW, FAN_MEDIUM, FAN_OFF

MANUAL_USER_MODE = 1
MAX_ACTUAL_FAN_LEVEL = 7
FAN_LEVEL_TO_MODE = {
    0: FAN_OFF,
    1: FAN_LOW,
    2: FAN_LOW,
    3: FAN_MEDIUM,
    4: FAN_HIGH,
    5: FAN_HIGH,
}


@dataclass(frozen=True)
class FanState:
    """Actual running state and its writable Climate fan-mode projection."""

    running: bool | None
    fan_mode: str | None


def coerce_fan_level(value: Any) -> int | None:
    """Return a canonical actual fan level when the value is valid."""
    try:
        numeric_value = float(value)
    except (TypeError, ValueError, OverflowError):
        return None
    if not isfinite(numeric_value) or not numeric_value.is_integer():
        return None
    level = int(numeric_value)
    return level if 0 <= level <= MAX_ACTUAL_FAN_LEVEL else None


def fan_mode_from_level(level: int | None) -> str | None:
    """Project an actual SAVE level onto the writable Climate fan modes."""
    return FAN_LEVEL_TO_MODE.get(level)


def _coerce_output(value: Any) -> float | None:
    """Return a numeric fan output without inventing an unavailable zero."""
    try:
        return None if value is None else float(value)
    except (TypeError, ValueError):
        return None


def resolve_fan_state(
    *,
    actual_level: Any,
    active_user_mode: Any,
    manual_level: Any,
    fan_outputs: tuple[Any, Any] | None = None,
) -> FanState:
    """Resolve running and discrete fan mode from actual transport readback."""
    actual = coerce_fan_level(actual_level)
    try:
        user_mode = int(float(active_user_mode))
    except (TypeError, ValueError):
        user_mode = None

    effective_level = actual
    if effective_level is None and user_mode == MANUAL_USER_MODE:
        effective_level = coerce_fan_level(manual_level)

    running: bool | None = None
    if fan_outputs is not None:
        outputs = tuple(_coerce_output(output) for output in fan_outputs)
        if any(output is not None and output > 0 for output in outputs):
            running = True
        elif all(output is not None and output == 0 for output in outputs):
            running = False
        elif all(output is None for output in outputs) and effective_level is not None:
            running = effective_level > 0
    elif effective_level is not None:
        running = effective_level > 0

    if running is False:
        return FanState(running=False, fan_mode=FAN_OFF)

    return FanState(running=running, fan_mode=fan_mode_from_level(effective_level))

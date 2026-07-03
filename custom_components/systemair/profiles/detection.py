"""Fail-safe device profile detection."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Protocol

from custom_components.systemair.profiles import DEVICE_PROFILE_LEGACY_D24810, DEVICE_PROFILE_SAVE

LOGGER = logging.getLogger(__name__)

SAVE_PROBE_REGISTERS = (1131, 1161, 1274, 2001)
D24810_PROBE_REGISTERS = (101, 108, 501, 601, 602)
D24810_SYSTEM_TYPES = {0, 1, 2, 3, 4, 5, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21}
SAVE_MINIMUM_SCORE = 3
D24810_MINIMUM_SCORE = 3


class ProfileDetectionError(Exception):
    """Raised when a profile cannot be detected safely."""


@dataclass(frozen=True)
class DetectionOutcome:
    """Result of profile auto-detection."""

    profile_id: str
    save_score: int
    d24810_score: int


class ProbeClient(Protocol):
    """Minimal async client protocol needed for profile probing."""

    async def read_registers(self, address_1based: int, count: int = 1) -> list[int]:
        """Read one or more one-based holding registers."""


def _value_in(values: dict[int, int], register: int, allowed: set[int]) -> bool:
    value = values.get(register)
    return value in allowed


def _value_between(values: dict[int, int], register: int, low: int, high: int) -> bool:
    value = values.get(register)
    return value is not None and low <= value <= high


def _score_save(values: dict[int, int]) -> int:
    score = 0
    if _value_in(values, 1131, {0, 2, 3, 4}):
        score += 1
    if _value_between(values, 1161, 0, 12):
        score += 1
    if _value_between(values, 1274, 0, 4):
        score += 1
    if _value_between(values, 2001, 120, 300):
        score += 1
    return score


def _score_d24810(values: dict[int, int]) -> int:
    if not _value_in(values, 501, D24810_SYSTEM_TYPES):
        return 0

    score = 2
    if _value_between(values, 101, 0, 4):
        score += 1
    if _value_in(values, 108, {0, 1}):
        score += 1
    if _value_between(values, 601, 1, 24):
        score += 1
    if _value_between(values, 602, 0, 3650):
        score += 1
    return score


def detect_profile_from_probe_values(*, save_values: dict[int, int], d24810_values: dict[int, int]) -> DetectionOutcome:
    """Detect a profile only when one profile clearly wins."""
    save_score = _score_save(save_values)
    d24810_score = _score_d24810(d24810_values)

    save_match = save_score >= SAVE_MINIMUM_SCORE
    d24810_match = d24810_score >= D24810_MINIMUM_SCORE

    if save_match and not d24810_match:
        return DetectionOutcome(profile_id=DEVICE_PROFILE_SAVE, save_score=save_score, d24810_score=d24810_score)
    if d24810_match and not save_match:
        return DetectionOutcome(profile_id=DEVICE_PROFILE_LEGACY_D24810, save_score=save_score, d24810_score=d24810_score)

    msg = f"Cannot auto-detect Systemair profile safely: save_score={save_score}, d24810_score={d24810_score}"
    raise ProfileDetectionError(msg)


async def _read_probe_registers(client: ProbeClient, registers: tuple[int, ...]) -> dict[int, int]:
    values: dict[int, int] = {}
    for register in registers:
        try:
            result = await client.read_registers(register, count=1)
        except Exception as err:  # noqa: BLE001 - probing must tolerate profile-mismatched registers.
            LOGGER.debug("Profile probe register %s failed: %s", register, err)
            continue
        if result:
            values[register] = int(result[0])
    return values


async def async_detect_profile(client: ProbeClient) -> DetectionOutcome:
    """Read minimal probes and detect the profile safely."""
    save_values = await _read_probe_registers(client, SAVE_PROBE_REGISTERS)
    d24810_values = await _read_probe_registers(client, D24810_PROBE_REGISTERS)
    return detect_profile_from_probe_values(save_values=save_values, d24810_values=d24810_values)

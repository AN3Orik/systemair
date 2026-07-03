"""Device profile registry."""

from __future__ import annotations

from typing import TYPE_CHECKING

from custom_components.systemair.profiles.d24810 import D24810_PROFILE
from custom_components.systemair.profiles.save import SAVE_PROFILE

if TYPE_CHECKING:
    from custom_components.systemair.profiles.base import DeviceProfile

DEVICE_PROFILE_AUTO = "auto"
DEVICE_PROFILE_SAVE = "save"
DEVICE_PROFILE_LEGACY_D24810 = "legacy_d24810"

_PROFILES: dict[str, DeviceProfile] = {
    DEVICE_PROFILE_SAVE: SAVE_PROFILE,
    DEVICE_PROFILE_LEGACY_D24810: D24810_PROFILE,
}


def get_device_profile(profile_id: str | None) -> DeviceProfile:
    """Return a device profile, defaulting old entries to SAVE."""
    if profile_id in (None, ""):
        return SAVE_PROFILE
    try:
        return _PROFILES[profile_id]
    except KeyError as err:
        msg = f"Unknown Systemair device profile: {profile_id}"
        raise ValueError(msg) from err


def iter_device_profiles() -> tuple[DeviceProfile, ...]:
    """Return all registered concrete device profiles."""
    return tuple(_PROFILES.values())

"""Custom integration to integrate Systemair VSR with Home Assistant."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.const import CONF_HOST, CONF_PORT, Platform
from homeassistant.loader import async_get_loaded_integration

from .api import SystemairVSRModbusClient
from .const import CONF_MODEL, CONF_SLAVE_ID
from .coordinator import SystemairDataUpdateCoordinator
from .data import SystemairConfigEntry, SystemairData

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant


PLATFORMS: list[Platform] = [
    Platform.CLIMATE,
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
    Platform.SWITCH,
    Platform.NUMBER,
    Platform.SELECT,
]


async def async_setup_entry(hass: HomeAssistant, entry: SystemairConfigEntry) -> bool:
    """Set up this integration using UI."""
    client = SystemairVSRModbusClient(
        host=entry.data[CONF_HOST],
        port=entry.data[CONF_PORT],
        slave_id=entry.data[CONF_SLAVE_ID],
    )
    await client.start()

    coordinator = SystemairDataUpdateCoordinator(hass=hass, client=client, config_entry=entry)

    model = entry.options.get(CONF_MODEL, entry.data.get(CONF_MODEL, "VSR 300"))

    entry.runtime_data = SystemairData(
        client=client,
        coordinator=coordinator,
        integration=async_get_loaded_integration(hass, entry.domain),
        model=model,
    )

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Handle removal of an entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        client: SystemairVSRModbusClient = entry.runtime_data.client
        await client.stop()

    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)

"""Custom integration to integrate Systemair VSR with Home Assistant."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.const import CONF_HOST, CONF_IP_ADDRESS, CONF_PORT, Platform
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.loader import async_get_loaded_integration

from .api import SystemairModbusClient, SystemairSerialClient, SystemairWebApiClient
from .const import (
    API_TYPE_MODBUS_SERIAL,
    API_TYPE_MODBUS_TCP,
    API_TYPE_MODBUS_WEBAPI,
    CONF_API_TYPE,
    CONF_BAUDRATE,
    CONF_BYTESIZE,
    CONF_MODEL,
    CONF_PARITY,
    CONF_SERIAL_PORT,
    CONF_SLAVE_ID,
    CONF_STOPBITS,
    CONF_WEB_API_MAX_REGISTERS,
    DEFAULT_WEB_API_MAX_REGISTERS,
)
from .coordinator import SystemairDataUpdateCoordinator
from .data import SystemairConfigEntry, SystemairData

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant


PLATFORMS: list[Platform] = [
    Platform.BUTTON,
    Platform.CLIMATE,
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
    Platform.SWITCH,
    Platform.NUMBER,
    Platform.SELECT,
]


async def async_setup_entry(hass: HomeAssistant, entry: SystemairConfigEntry) -> bool:
    """Set up this integration using UI."""
    api_type = entry.data.get(CONF_API_TYPE, API_TYPE_MODBUS_TCP)

    if api_type == API_TYPE_MODBUS_WEBAPI:
        max_registers = entry.options.get(CONF_WEB_API_MAX_REGISTERS, DEFAULT_WEB_API_MAX_REGISTERS)
        client = SystemairWebApiClient(
            address=entry.data[CONF_IP_ADDRESS],
            session=async_get_clientsession(hass),
            max_registers_per_request=max_registers,
        )
    elif api_type == API_TYPE_MODBUS_SERIAL:
        client = SystemairSerialClient(
            port=entry.data[CONF_SERIAL_PORT],
            baudrate=entry.data[CONF_BAUDRATE],
            bytesize=entry.data[CONF_BYTESIZE],
            parity=entry.data[CONF_PARITY],
            stopbits=entry.data[CONF_STOPBITS],
            slave_id=entry.data[CONF_SLAVE_ID],
        )
        await client.start()
    else:
        # Default to Modbus TCP
        client = SystemairModbusClient(
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
        api_type=api_type,
    )

    if api_type == API_TYPE_MODBUS_WEBAPI:
        await coordinator.async_setup_webapi()
        await coordinator.async_config_entry_first_refresh()
    else:
        # For Modbus TCP, just start normal updates
        pass

    entry.async_on_unload(entry.add_update_listener(async_options_update_listener))

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_options_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options update."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Handle removal of an entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        api_type = entry.data.get(CONF_API_TYPE, API_TYPE_MODBUS_TCP)
        if api_type in (API_TYPE_MODBUS_TCP, API_TYPE_MODBUS_SERIAL):
            client = entry.runtime_data.client
            await client.stop()

    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)

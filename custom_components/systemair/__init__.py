"""Custom integration to integrate Systemair VSR with Home Assistant."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.const import (
    CONF_HOST,
    CONF_IP_ADDRESS,
    CONF_PASSWORD,
    CONF_PORT,
    CONF_USERNAME,
    Platform,
)
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.loader import async_get_loaded_integration

from .api import SystemairModbusClient, SystemairSerialClient, SystemairWebApiClient
from .const import (
    API_TYPE_HOMESOLUTION,
    API_TYPE_MODBUS_SERIAL,
    API_TYPE_MODBUS_TCP,
    API_TYPE_MODBUS_WEBAPI,
    CONF_API_TYPE,
    CONF_BAUDRATE,
    CONF_BYTESIZE,
    CONF_DEVICE_ID,
    CONF_DEVICE_PROFILE,
    CONF_MODEL,
    CONF_PARITY,
    CONF_SERIAL_PORT,
    CONF_SLAVE_ID,
    CONF_STOPBITS,
    CONF_UPDATE_INTERVAL,
    CONF_WEB_API_MAX_REGISTERS,
    DEFAULT_UPDATE_INTERVAL,
    DEFAULT_WEB_API_MAX_REGISTERS,
    LOGGER,
)
from .coordinator import SystemairDataUpdateCoordinator
from .data import SystemairConfigEntry, SystemairData
from .homesolution import SystemairHomeSolutionClient
from .profiles import get_device_profile

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant

    from .profiles.base import DeviceProfile


PLATFORMS: list[Platform] = [
    Platform.BUTTON,
    Platform.CLIMATE,
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
    Platform.SWITCH,
    Platform.NUMBER,
    Platform.SELECT,
]


def _profile_platforms(profile: DeviceProfile) -> list[Platform]:
    """Return Home Assistant platforms supported by a profile."""
    return list(profile.supported_platforms)


def _profile_supports_api_type(profile: DeviceProfile, api_type: str) -> bool:
    """Return whether a profile can run on a connection mode."""
    return api_type in profile.supported_api_types


async def async_setup_entry(hass: HomeAssistant, entry: SystemairConfigEntry) -> bool:
    """Set up this integration using UI."""
    api_type = entry.data.get(CONF_API_TYPE, API_TYPE_MODBUS_TCP)
    try:
        profile = get_device_profile(entry.data.get(CONF_DEVICE_PROFILE))
    except ValueError as err:
        LOGGER.error("Unable to set up Systemair entry %s: %s", entry.entry_id, err)
        return False

    if not _profile_supports_api_type(profile, api_type):
        LOGGER.error(
            "Systemair profile %s does not support connection mode %s for entry %s",
            profile.profile_id,
            api_type,
            entry.entry_id,
        )
        return False

    if api_type == API_TYPE_MODBUS_WEBAPI:
        max_registers = entry.options.get(CONF_WEB_API_MAX_REGISTERS, DEFAULT_WEB_API_MAX_REGISTERS)
        client = SystemairWebApiClient(
            address=entry.data[CONF_IP_ADDRESS],
            session=async_get_clientsession(hass),
            max_registers_per_request=max_registers,
            password=entry.data.get(CONF_PASSWORD) or None,
        )
    elif api_type == API_TYPE_MODBUS_SERIAL:
        client = SystemairSerialClient(
            port=entry.data[CONF_SERIAL_PORT],
            baudrate=entry.data[CONF_BAUDRATE],
            bytesize=entry.data[CONF_BYTESIZE],
            parity=entry.data[CONF_PARITY],
            stopbits=entry.data[CONF_STOPBITS],
            slave_id=entry.data[CONF_SLAVE_ID],
            read_blocks=profile.read_blocks,
            alarm_detail_blocks=profile.alarm_detail_blocks,
            alarm_history_blocks=profile.alarm_history_blocks,
            test_register=profile.test_register,
        )
        await client.start()
    elif api_type == API_TYPE_HOMESOLUTION:
        client = SystemairHomeSolutionClient(
            username=entry.data[CONF_USERNAME],
            password=entry.data[CONF_PASSWORD],
            device_id=entry.data[CONF_DEVICE_ID],
        )
        await client.start()
    else:
        # Default to Modbus TCP
        client = SystemairModbusClient(
            host=entry.data[CONF_HOST],
            port=entry.data[CONF_PORT],
            slave_id=entry.data[CONF_SLAVE_ID],
            read_blocks=profile.read_blocks,
            alarm_detail_blocks=profile.alarm_detail_blocks,
            alarm_history_blocks=profile.alarm_history_blocks,
            test_register=profile.test_register,
        )
        await client.start()

    update_interval = entry.options.get(CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL)
    coordinator = SystemairDataUpdateCoordinator(
        hass=hass,
        client=client,
        config_entry=entry,
        update_interval_seconds=update_interval,
    )

    model = entry.options.get(CONF_MODEL, entry.data.get(CONF_MODEL, "VSR 300"))

    entry.runtime_data = SystemairData(
        client=client,
        coordinator=coordinator,
        integration=async_get_loaded_integration(hass, entry.domain),
        model=model,
        api_type=api_type,
        profile=profile,
    )

    if api_type == API_TYPE_MODBUS_WEBAPI:
        await coordinator.async_setup_webapi()
        await coordinator.async_config_entry_first_refresh()
    else:
        # For Modbus TCP, just start normal updates
        pass

    entry.async_on_unload(entry.add_update_listener(async_options_update_listener))

    await hass.config_entries.async_forward_entry_setups(entry, _profile_platforms(profile))

    return True


async def async_options_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options update."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Handle removal of an entry."""
    profile = getattr(entry.runtime_data, "profile", None)
    if profile is None:
        try:
            profile = get_device_profile(entry.data.get(CONF_DEVICE_PROFILE))
        except ValueError as err:
            LOGGER.warning("Unable to resolve Systemair profile while unloading entry %s: %s", entry.entry_id, err)

    unload_platforms = _profile_platforms(profile) if profile is not None else PLATFORMS
    unload_ok = await hass.config_entries.async_unload_platforms(entry, unload_platforms)

    if unload_ok:
        api_type = entry.data.get(CONF_API_TYPE, API_TYPE_MODBUS_TCP)
        if api_type in (API_TYPE_MODBUS_TCP, API_TYPE_MODBUS_SERIAL, API_TYPE_HOMESOLUTION):
            client = entry.runtime_data.client
            await client.stop()

    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)

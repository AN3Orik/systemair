"""Config flow for Systemair VSR integration."""

from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import callback
from homeassistant.helpers import selector

from .api import ModbusConnectionError, SystemairVSRModbusClient
from .const import (
    CONF_MODEL,
    CONF_SLAVE_ID,
    DEFAULT_PORT,
    DEFAULT_SLAVE_ID,
    DOMAIN,
    LOGGER,
    MODEL_SPECS,
)


class SystemairVSRConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Systemair VSR."""

    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(
        _config_entry: config_entries.ConfigEntry,
    ) -> SystemairOptionsFlowHandler:
        """Get the options flow for this handler."""
        return SystemairOptionsFlowHandler()

    async def _validate_connection(self, user_input: dict) -> None:
        """Validate the connection to the VSR unit."""
        client = SystemairVSRModbusClient(
            host=user_input[CONF_HOST],
            port=user_input[CONF_PORT],
            slave_id=user_input[CONF_SLAVE_ID],
        )
        if not await client.test_connection():
            msg = "Failed to connect"
            raise ModbusConnectionError(msg)

    async def async_step_user(self, user_input: dict | None = None) -> config_entries.ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                await self._validate_connection(user_input)
            except ModbusConnectionError as e:
                LOGGER.error("Failed to connect to VSR unit: %s", e)
                errors["base"] = "cannot_connect"
            except (TimeoutError, OSError) as e:
                LOGGER.exception("Unexpected exception: %s", e)
                errors["base"] = "unknown"
            else:
                unique_id = f"{user_input[CONF_HOST]}:{user_input[CONF_PORT]}"
                await self.async_set_unique_id(unique_id)
                self._abort_if_unique_id_configured()

                return self.async_create_entry(title=user_input[CONF_HOST], data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_HOST): selector.TextSelector(),
                    vol.Required(CONF_PORT, default=DEFAULT_PORT): vol.Coerce(int),
                    vol.Required(CONF_SLAVE_ID, default=DEFAULT_SLAVE_ID): vol.Coerce(int),
                    vol.Required(CONF_MODEL, default=next(iter(MODEL_SPECS))): selector.SelectSelector(
                        selector.SelectSelectorConfig(
                            options=list(MODEL_SPECS.keys()),
                            mode=selector.SelectSelectorMode.DROPDOWN,
                        )
                    ),
                }
            ),
            errors=errors,
        )


class SystemairOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle an options flow for Systemair."""

    @property
    def config_entry(self) -> config_entries.ConfigEntry:
        """Return the config entry for this flow."""
        return self.hass.config_entries.async_get_entry(self.handler)

    async def async_step_init(self, user_input: dict | None = None) -> config_entries.ConfigFlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        default_model = self.config_entry.options.get(CONF_MODEL, self.config_entry.data.get(CONF_MODEL, "VSR 300"))

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_MODEL, default=default_model): selector.SelectSelector(
                        selector.SelectSelectorConfig(
                            options=list(MODEL_SPECS.keys()),
                            mode=selector.SelectSelectorMode.DROPDOWN,
                        )
                    ),
                }
            ),
        )

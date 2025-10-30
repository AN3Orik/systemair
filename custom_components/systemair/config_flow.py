"""Config flow for Systemair VSR integration."""

from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_IP_ADDRESS, CONF_PORT
from homeassistant.core import callback
from homeassistant.helpers import selector
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import (
    ModbusConnectionError,
    SystemairApiClientCommunicationError,
    SystemairApiClientError,
    SystemairModbusClient,
    SystemairSerialClient,
    SystemairWebApiClient,
)
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
    DEFAULT_BAUDRATE,
    DEFAULT_BYTESIZE,
    DEFAULT_PARITY,
    DEFAULT_PORT,
    DEFAULT_SERIAL_PORT,
    DEFAULT_SLAVE_ID,
    DEFAULT_STOPBITS,
    DEFAULT_WEB_API_MAX_REGISTERS,
    DOMAIN,
    LOGGER,
    MODEL_SPECS,
    SERIAL_BAUDRATES,
    SERIAL_BYTESIZES,
    SERIAL_PARITIES,
    SERIAL_STOPBITS,
)


class SystemairVSRConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Systemair VSR."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._api_type: str | None = None

    @staticmethod
    @callback
    def async_get_options_flow(
        _config_entry: config_entries.ConfigEntry,
    ) -> SystemairOptionsFlowHandler:
        """Get the options flow for this handler."""
        return SystemairOptionsFlowHandler()

    async def _validate_modbus_tcp_connection(self, user_input: dict) -> None:
        """Validate the connection to the unit via Modbus TCP."""
        client = SystemairModbusClient(
            host=user_input[CONF_HOST],
            port=user_input[CONF_PORT],
            slave_id=user_input[CONF_SLAVE_ID],
        )
        if not await client.test_connection():
            msg = "Failed to connect"
            raise ModbusConnectionError(msg)

    async def _validate_serial_connection(self, user_input: dict) -> None:
        """Validate the connection to the unit via Modbus Serial."""
        baudrate = int(user_input[CONF_BAUDRATE])

        bytesize = user_input[CONF_BYTESIZE]
        if bytesize in SERIAL_BYTESIZES:
            bytesize = SERIAL_BYTESIZES[bytesize]

        parity = user_input[CONF_PARITY]
        if parity in SERIAL_PARITIES:
            parity = SERIAL_PARITIES[parity]

        stopbits = user_input[CONF_STOPBITS]
        if stopbits in SERIAL_STOPBITS:
            stopbits = SERIAL_STOPBITS[stopbits]

        client = SystemairSerialClient(
            port=user_input[CONF_SERIAL_PORT],
            baudrate=baudrate,
            bytesize=bytesize,
            parity=parity,
            stopbits=stopbits,
            slave_id=user_input[CONF_SLAVE_ID],
        )
        try:
            await client.start()
            if not await client.test_connection():
                msg = "Failed to connect"
                raise ModbusConnectionError(msg)
        finally:
            await client.stop()

    async def _validate_webapi_connection(self, user_input: dict) -> dict[str, str]:
        """Validate the connection via Web API and return device info."""
        client = SystemairWebApiClient(
            address=user_input[CONF_IP_ADDRESS],
            session=async_get_clientsession(self.hass),
        )
        menu = await client.async_get_endpoint("menu")
        unit_version = await client.async_get_endpoint("unit_version")

        response = {}
        response["mac_address"] = menu["mac"]
        response["model"] = unit_version["MB Model"]
        return response

    async def async_step_user(self, user_input: dict | None = None) -> config_entries.ConfigFlowResult:
        """Handle the initial step - select API type."""
        if user_input is not None:
            self._api_type = user_input[CONF_API_TYPE]

            if self._api_type == API_TYPE_MODBUS_TCP:
                return await self.async_step_modbus_tcp()
            if self._api_type == API_TYPE_MODBUS_SERIAL:
                return await self.async_step_modbus_serial()
            return await self.async_step_modbus_webapi()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_API_TYPE, default=API_TYPE_MODBUS_TCP): selector.SelectSelector(
                        selector.SelectSelectorConfig(
                            options=[
                                selector.SelectOptionDict(value=API_TYPE_MODBUS_TCP, label="Modbus TCP"),
                                selector.SelectOptionDict(value=API_TYPE_MODBUS_WEBAPI, label="Modbus WebAPI (HTTP)"),
                                selector.SelectOptionDict(value=API_TYPE_MODBUS_SERIAL, label="Modbus Serial (RS485)"),
                            ],
                            mode=selector.SelectSelectorMode.DROPDOWN,
                        )
                    ),
                }
            ),
        )

    async def async_step_modbus_tcp(self, user_input: dict | None = None) -> config_entries.ConfigFlowResult:
        """Handle Modbus TCP configuration."""
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                await self._validate_modbus_tcp_connection(user_input)
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

                user_input[CONF_API_TYPE] = API_TYPE_MODBUS_TCP
                return self.async_create_entry(
                    title=user_input.get(CONF_MODEL, user_input[CONF_HOST]),
                    data=user_input,
                )

        return self.async_show_form(
            step_id="modbus_tcp",
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

    async def async_step_modbus_serial(self, user_input: dict | None = None) -> config_entries.ConfigFlowResult:
        """Handle Modbus Serial configuration."""
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                await self._validate_serial_connection(user_input)
            except ModbusConnectionError as e:
                LOGGER.error("Failed to connect to VSR unit via Serial: %s", e)
                errors["base"] = "cannot_connect"
            except (TimeoutError, OSError) as e:
                LOGGER.exception("Unexpected exception: %s", e)
                errors["base"] = "unknown"
            else:
                unique_id = f"serial_{user_input[CONF_SERIAL_PORT]}"
                await self.async_set_unique_id(unique_id)
                self._abort_if_unique_id_configured()

                user_input[CONF_API_TYPE] = API_TYPE_MODBUS_SERIAL

                # Convert display values to serial library constants
                user_input[CONF_BAUDRATE] = int(user_input[CONF_BAUDRATE])

                if user_input[CONF_BYTESIZE] in SERIAL_BYTESIZES:
                    user_input[CONF_BYTESIZE] = SERIAL_BYTESIZES[user_input[CONF_BYTESIZE]]

                if user_input[CONF_PARITY] in SERIAL_PARITIES:
                    user_input[CONF_PARITY] = SERIAL_PARITIES[user_input[CONF_PARITY]]

                if user_input[CONF_STOPBITS] in SERIAL_STOPBITS:
                    user_input[CONF_STOPBITS] = SERIAL_STOPBITS[user_input[CONF_STOPBITS]]

                return self.async_create_entry(
                    title=user_input.get(CONF_MODEL, f"Serial {user_input[CONF_SERIAL_PORT]}"),
                    data=user_input,
                )

        return self.async_show_form(
            step_id="modbus_serial",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_SERIAL_PORT, default=DEFAULT_SERIAL_PORT): selector.TextSelector(),
                    vol.Required(CONF_BAUDRATE, default=str(DEFAULT_BAUDRATE)): selector.SelectSelector(
                        selector.SelectSelectorConfig(
                            options=[str(b) for b in SERIAL_BAUDRATES],
                            mode=selector.SelectSelectorMode.DROPDOWN,
                        )
                    ),
                    vol.Required(CONF_BYTESIZE, default=DEFAULT_BYTESIZE): selector.SelectSelector(
                        selector.SelectSelectorConfig(
                            options=list(SERIAL_BYTESIZES.keys()),
                            mode=selector.SelectSelectorMode.DROPDOWN,
                        )
                    ),
                    vol.Required(CONF_PARITY, default=DEFAULT_PARITY): selector.SelectSelector(
                        selector.SelectSelectorConfig(
                            options=list(SERIAL_PARITIES.keys()),
                            mode=selector.SelectSelectorMode.DROPDOWN,
                        )
                    ),
                    vol.Required(CONF_STOPBITS, default=DEFAULT_STOPBITS): selector.SelectSelector(
                        selector.SelectSelectorConfig(
                            options=list(SERIAL_STOPBITS.keys()),
                            mode=selector.SelectSelectorMode.DROPDOWN,
                        )
                    ),
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

    async def async_step_modbus_webapi(self, user_input: dict | None = None) -> config_entries.ConfigFlowResult:
        """Handle Modbus WebAPI configuration."""
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                device_info = await self._validate_webapi_connection(user_input)
            except SystemairApiClientCommunicationError as exception:
                LOGGER.error(exception)
                errors["base"] = "cannot_connect"
            except SystemairApiClientError as exception:
                LOGGER.exception(exception)
                errors["base"] = "unknown"
            else:
                await self.async_set_unique_id(device_info["mac_address"])
                self._abort_if_unique_id_configured()

                user_input[CONF_API_TYPE] = API_TYPE_MODBUS_WEBAPI

                # Use device model if user didn't select one manually
                if CONF_MODEL not in user_input or not user_input[CONF_MODEL]:
                    user_input[CONF_MODEL] = device_info.get("model", next(iter(MODEL_SPECS)))

                # Title is always the selected/detected model
                return self.async_create_entry(
                    title=user_input[CONF_MODEL],
                    data=user_input,
                )

        return self.async_show_form(
            step_id="modbus_webapi",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_IP_ADDRESS): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.TEXT,
                        )
                    ),
                    vol.Optional(CONF_MODEL): selector.SelectSelector(
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
            # Update the integration title to match selected model
            new_model = user_input.get(CONF_MODEL)
            if new_model:
                self.hass.config_entries.async_update_entry(
                    self.config_entry,
                    title=new_model,
                )
            return self.async_create_entry(title="", data=user_input)

        default_model = self.config_entry.options.get(CONF_MODEL, self.config_entry.data.get(CONF_MODEL, "VSR 300"))
        api_type = self.config_entry.data.get(CONF_API_TYPE)

        # Base schema with model selection
        schema_dict = {
            vol.Required(CONF_MODEL, default=default_model): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=list(MODEL_SPECS.keys()),
                    mode=selector.SelectSelectorMode.DROPDOWN,
                )
            ),
        }

        # Web API specific options
        if api_type == API_TYPE_MODBUS_WEBAPI:
            default_max_registers = self.config_entry.options.get(CONF_WEB_API_MAX_REGISTERS, DEFAULT_WEB_API_MAX_REGISTERS)
            schema_dict[vol.Optional(CONF_WEB_API_MAX_REGISTERS, default=default_max_registers)] = selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=30,
                    max=125,
                    mode=selector.NumberSelectorMode.BOX,
                )
            )

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(schema_dict),
        )

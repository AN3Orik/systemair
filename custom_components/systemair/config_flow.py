"""Config flow for Systemair VSR integration."""

from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_IP_ADDRESS, CONF_PASSWORD, CONF_PORT, CONF_USERNAME
from homeassistant.core import callback
from homeassistant.helpers import selector
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import (
    ModbusConnectionError,
    SystemairApiClientCommunicationError,
    SystemairApiClientError,
    SystemairAuthError,
    SystemairAuthRequiredError,
    SystemairModbusClient,
    SystemairSerialClient,
    SystemairWebApiClient,
)
from .const import (
    API_TYPE_HOMESOLUTION,
    API_TYPE_MODBUS_SERIAL,
    API_TYPE_MODBUS_TCP,
    API_TYPE_MODBUS_WEBAPI,
    CONF_API_TYPE,
    CONF_BAUDRATE,
    CONF_BYTESIZE,
    CONF_DEVICE_ID,
    CONF_ENABLE_ALARM_DETAILS,
    CONF_ENABLE_ALARM_HISTORY,
    CONF_MODEL,
    CONF_PARITY,
    CONF_SERIAL_PORT,
    CONF_SLAVE_ID,
    CONF_STOPBITS,
    CONF_UPDATE_INTERVAL,
    CONF_WEB_API_MAX_REGISTERS,
    DEFAULT_BAUDRATE,
    DEFAULT_BYTESIZE,
    DEFAULT_PARITY,
    DEFAULT_PORT,
    DEFAULT_SERIAL_PORT,
    DEFAULT_SLAVE_ID,
    DEFAULT_STOPBITS,
    DEFAULT_UPDATE_INTERVAL,
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
        self._homesolution_creds: dict[str, Any] = {}
        self._homesolution_devices: list[dict[str, Any]] = []
        self._reauth_entry_data: dict[str, Any] = {}

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
        """
        Validate the connection via Web API and return device info.

        Probes /auth/status first. If the device has a password configured,
        the supplied password is required and is verified by performing a real
        authenticated /mread of register 1131 (REG_USERMODE_MANUAL_AIRFLOW_LEVEL_SAF).
        """
        client = SystemairWebApiClient(
            address=user_input[CONF_IP_ADDRESS],
            session=async_get_clientsession(self.hass),
            password=user_input.get(CONF_PASSWORD) or None,
        )

        menu = await client.async_get_endpoint("menu")
        unit_version = await client.async_get_endpoint("unit_version")

        if client._password is not None:  # noqa: SLF001 — verifying creds before persisting
            await client._ensure_authenticated(force=True)  # noqa: SLF001
            if not await client.test_connection():
                msg = "Authenticated test read failed"
                raise SystemairApiClientCommunicationError(msg)

        return {
            "mac_address": menu["mac"],
            "model": unit_version["MB Model"],
        }

    async def _webapi_status(self, ip_address: str) -> dict[str, Any]:
        """Read /auth/status to decide whether to ask for a password."""
        client = SystemairWebApiClient(
            address=ip_address,
            session=async_get_clientsession(self.hass),
        )
        response = await client.async_get_endpoint("auth/status")
        return response if isinstance(response, dict) else {}

    async def _get_homesolution_devices(self, user_input: dict) -> list[dict[str, Any]]:
        """Validate HomeSolution credentials and get list of devices."""
        # We need to import here to avoid circular imports or if the library is optional
        from .systemair_api import (  # noqa: PLC0415
            SystemairAPI,
            SystemairAuthenticator,
        )
        from .systemair_api.utils.exceptions import (  # noqa: PLC0415
            AuthenticationError,
            SystemairError,
        )

        authenticator = SystemairAuthenticator(
            email=user_input[CONF_USERNAME],
            password=user_input[CONF_PASSWORD],
        )

        try:
            await self.hass.async_add_executor_job(authenticator.authenticate)
        except AuthenticationError as e:
            msg = "invalid_auth"
            raise ValueError(msg) from e
        except SystemairError as e:
            msg = "cannot_connect"
            raise ValueError(msg) from e

        api = SystemairAPI(access_token=authenticator.access_token)

        try:
            devices_response = await self.hass.async_add_executor_job(api.get_account_devices)
        except SystemairError as e:
            msg = "cannot_connect"
            raise ValueError(msg) from e

        # Logic adapted from HomeSolution coordinator
        data = devices_response.get("data", {})
        devices = []
        if "GetAccountDevices" in data:
            devices = data.get("GetAccountDevices", [])
        elif "account" in data and "devices" in data.get("account", {}):
            devices = data.get("account", {}).get("devices", [])

        if not devices:
            msg = "no_devices_found"
            raise ValueError(msg)

        return devices

    async def async_step_user(self, user_input: dict | None = None) -> config_entries.ConfigFlowResult:
        """Handle the initial step - select API type."""
        if user_input is not None:
            self._api_type = user_input[CONF_API_TYPE]

            if self._api_type == API_TYPE_MODBUS_TCP:
                return await self.async_step_modbus_tcp()
            if self._api_type == API_TYPE_MODBUS_SERIAL:
                return await self.async_step_modbus_serial()
            if self._api_type == API_TYPE_HOMESOLUTION:
                return await self.async_step_homesolution()
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
                                selector.SelectOptionDict(value=API_TYPE_HOMESOLUTION, label="HomeSolution (Cloud)"),
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

    async def async_step_modbus_webapi(  # noqa: PLR0912
        self, user_input: dict | None = None
    ) -> config_entries.ConfigFlowResult:
        """Handle Modbus WebAPI configuration."""
        errors: dict[str, str] = {}
        require_password = False

        if user_input is not None:
            ip_address = user_input.get(CONF_IP_ADDRESS, "").strip()
            try:
                status = await self._webapi_status(ip_address)
            except SystemairApiClientCommunicationError as exception:
                LOGGER.error("Cannot reach %s: %s", ip_address, exception)
                errors["base"] = "cannot_connect"
            except SystemairApiClientError as exception:
                LOGGER.exception(exception)
                errors["base"] = "unknown"
            else:
                require_password = bool(status.get("configured", False))
                if require_password and not user_input.get(CONF_PASSWORD):
                    errors["base"] = "password_required"
                else:
                    try:
                        device_info = await self._validate_webapi_connection(user_input)
                    except SystemairAuthRequiredError as exception:
                        LOGGER.error(exception)
                        errors["base"] = "password_not_set"
                    except SystemairAuthError as exception:
                        LOGGER.error(exception)
                        errors["base"] = "invalid_auth"
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

                        # Strip empty password so we don't persist it
                        if not user_input.get(CONF_PASSWORD):
                            user_input.pop(CONF_PASSWORD, None)

                        return self.async_create_entry(
                            title=user_input[CONF_MODEL],
                            data=user_input,
                        )

        schema_dict: dict[Any, Any] = {
            vol.Required(CONF_IP_ADDRESS, default=(user_input or {}).get(CONF_IP_ADDRESS, "")): selector.TextSelector(
                selector.TextSelectorConfig(type=selector.TextSelectorType.TEXT)
            ),
        }
        if require_password or (user_input is not None and CONF_PASSWORD in user_input):
            schema_dict[vol.Required(CONF_PASSWORD)] = selector.TextSelector(
                selector.TextSelectorConfig(type=selector.TextSelectorType.PASSWORD)
            )
        else:
            schema_dict[vol.Optional(CONF_PASSWORD)] = selector.TextSelector(
                selector.TextSelectorConfig(type=selector.TextSelectorType.PASSWORD)
            )
        schema_dict[vol.Optional(CONF_MODEL)] = selector.SelectSelector(
            selector.SelectSelectorConfig(
                options=list(MODEL_SPECS.keys()),
                mode=selector.SelectSelectorMode.DROPDOWN,
            )
        )

        return self.async_show_form(
            step_id="modbus_webapi",
            data_schema=vol.Schema(schema_dict),
            errors=errors,
        )

    async def async_step_reauth(self, entry_data: dict[str, Any]) -> config_entries.ConfigFlowResult:
        """Trigger reauth — typically because /auth/login started rejecting the stored password."""
        self._reauth_entry_data = dict(entry_data)
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(self, user_input: dict | None = None) -> config_entries.ConfigFlowResult:
        """Prompt for a fresh password and verify it against the device."""
        errors: dict[str, str] = {}
        entry = self._get_reauth_entry()

        if user_input is not None:
            merged = {**self._reauth_entry_data, CONF_PASSWORD: user_input[CONF_PASSWORD]}
            try:
                await self._validate_webapi_connection(merged)
            except SystemairAuthRequiredError as exception:
                LOGGER.error(exception)
                errors["base"] = "password_not_set"
            except SystemairAuthError as exception:
                LOGGER.error(exception)
                errors["base"] = "invalid_auth"
            except SystemairApiClientCommunicationError as exception:
                LOGGER.error(exception)
                errors["base"] = "cannot_connect"
            except SystemairApiClientError as exception:
                LOGGER.exception(exception)
                errors["base"] = "unknown"
            else:
                self.hass.config_entries.async_update_entry(
                    entry,
                    data={**entry.data, CONF_PASSWORD: user_input[CONF_PASSWORD]},
                )
                await self.hass.config_entries.async_reload(entry.entry_id)
                return self.async_abort(reason="reauth_successful")

        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_PASSWORD): selector.TextSelector(
                        selector.TextSelectorConfig(type=selector.TextSelectorType.PASSWORD)
                    ),
                }
            ),
            errors=errors,
        )

    def _get_reauth_entry(self) -> config_entries.ConfigEntry:
        """Resolve the config entry that triggered the reauth."""
        entry_id = self.context.get("entry_id")
        if entry_id is not None:
            entry = self.hass.config_entries.async_get_entry(entry_id)
            if entry is not None:
                return entry
        msg = "Reauth flow has no associated config entry"
        raise RuntimeError(msg)

    async def async_step_homesolution(self, user_input: dict | None = None) -> config_entries.ConfigFlowResult:
        """Handle HomeSolution configuration."""
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                devices = await self._get_homesolution_devices(user_input)
            except ValueError as e:
                errors["base"] = str(e)
            except Exception:  # noqa: BLE001
                LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                self._homesolution_creds = user_input
                self._homesolution_devices = devices
                return await self.async_step_homesolution_device()

        return self.async_show_form(
            step_id="homesolution",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_USERNAME): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.EMAIL,
                        )
                    ),
                    vol.Required(CONF_PASSWORD): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.PASSWORD,
                        )
                    ),
                }
            ),
            errors=errors,
        )

    async def async_step_homesolution_device(self, user_input: dict | None = None) -> config_entries.ConfigFlowResult:
        """Handle HomeSolution device selection."""
        if user_input is not None:
            device_id = user_input[CONF_DEVICE_ID]
            selected_device = next((d for d in self._homesolution_devices if (d.get("identifier") or d.get("id")) == device_id), None)

            if selected_device:
                await self.async_set_unique_id(device_id)
                self._abort_if_unique_id_configured()

                data = {
                    **self._homesolution_creds,
                    CONF_API_TYPE: API_TYPE_HOMESOLUTION,
                    CONF_DEVICE_ID: device_id,
                }

                return self.async_create_entry(
                    title=selected_device.get("name", "Systemair Unit"),
                    data=data,
                )

        options = []
        for device in self._homesolution_devices:
            d_id = device.get("identifier") or device.get("id")
            d_name = device.get("name", d_id)
            options.append(selector.SelectOptionDict(value=d_id, label=d_name))

        return self.async_show_form(
            step_id="homesolution_device",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_DEVICE_ID): selector.SelectSelector(
                        selector.SelectSelectorConfig(
                            options=options,
                            mode=selector.SelectSelectorMode.DROPDOWN,
                        )
                    ),
                }
            ),
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

        # Get current update interval & alarm options
        # WebAPI (SAVECONNECT 2.0) has these disabled by default to prevent hangs
        is_webapi = api_type == API_TYPE_MODBUS_WEBAPI
        default_update_interval = self.config_entry.options.get(CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL)
        default_alarm_details = self.config_entry.options.get(CONF_ENABLE_ALARM_DETAILS, not is_webapi)
        default_alarm_history = self.config_entry.options.get(CONF_ENABLE_ALARM_HISTORY, not is_webapi)

        # Base schema with model selection and update interval
        schema_dict = {
            vol.Required(CONF_MODEL, default=default_model): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=list(MODEL_SPECS.keys()),
                    mode=selector.SelectSelectorMode.DROPDOWN,
                )
            ),
            vol.Optional(CONF_UPDATE_INTERVAL, default=default_update_interval): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=10,
                    max=120,
                    step=1,
                    mode=selector.NumberSelectorMode.BOX,
                    unit_of_measurement="s",
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

        schema_dict[vol.Optional(CONF_ENABLE_ALARM_DETAILS, default=default_alarm_details)] = selector.BooleanSelector()
        schema_dict[vol.Optional(CONF_ENABLE_ALARM_HISTORY, default=default_alarm_history)] = selector.BooleanSelector()

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(schema_dict),
        )

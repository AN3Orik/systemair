"""Ventilation unit model."""

from typing import Any

from custom_components.systemair.systemair_api.api.systemair_api import SystemairAPI
from custom_components.systemair.systemair_api.utils.constants import UserModes
from custom_components.systemair.systemair_api.utils.register_constants import RegisterConstants

from .ventilation_data import VentilationData


class VentilationUnit:
    """Model representing a Systemair ventilation unit."""

    def __init__(self, identifier: str, name: str) -> None:
        """Initialize a ventilation unit with a unique identifier and name."""
        self.identifier: str = identifier
        self.name: str = name
        self.model: str | None = None
        self.active_alarms: bool = False
        self.airflow: int | None = None
        self.connectivity: list[str] = []
        self.filter_expiration: int | None = None
        self.serial_number: str | None = None
        self.temperature: float | None = None
        self.user_mode: int | None = None
        self.air_quality: int | None = None
        self.humidity: int | None = None
        self.co2: int | None = None
        self.update_in_progress: bool = False
        self.configuration_wizard_active: bool = False
        self.user_mode_remaining_time: int | None = None
        self.user_mode_times: dict[str, int | None] = {
            "holiday": None,  # REG_MAINBOARD_USERMODE_HOLIDAY_TIME
            "away": None,  # REG_MAINBOARD_USERMODE_AWAY_TIME
            "fireplace": None,  # REG_MAINBOARD_USERMODE_FIREPLACE_TIME
            "refresh": None,  # REG_MAINBOARD_USERMODE_REFRESH_TIME
            "crowded": None,  # REG_MAINBOARD_USERMODE_CROWDED_TIME
        }
        self.temperatures: dict[str, float | None] = {
            "oat": None,  # Outdoor Air Temperature
            "sat": None,  # Supply Air Temperature
            "setpoint": None,
        }
        self.versions: list[dict[str, str]] = []

        # All raw registers
        self.registers: dict[int, Any] = {}

        # Attributes from API data
        self.eco_mode: int | None = None
        self.locked_user: int | None = None
        self.alarm_type_a: int | None = None
        self.alarm_type_b: int | None = None
        self.alarm_type_c: int | None = None
        self.suw_required: int | None = None
        self.reheater_type: int | None = None
        self.active_functions: dict[str, bool] = {
            "cooling": False,
            "free_cooling": False,
            "heating": False,
            "defrosting": False,
            "heat_recovery": False,
            "cooling_recovery": False,
            "moisture_transfer": False,
            "secondary_air": False,
            "vacuum_cleaner": False,
            "cooker_hood": False,
            "user_lock": False,
            "eco_mode": False,
            "heater_cool_down": False,
            "pressure_guard": False,
            "cdi_1": False,
            "cdi_2": False,
            "cdi_3": False,
        }

    def update_from_api(self, api_data: dict[str, Any]) -> None:
        """Update the ventilation unit with data from the API."""
        if "data" in api_data and "GetView" in api_data["data"]:
            children = api_data["data"]["GetView"]["children"]
            for child in children:
                if "properties" in child and "dataItem" in child["properties"]:
                    data_item = child["properties"]["dataItem"]
                    self._update_attribute(data_item)

    def _update_attribute(self, data_item: dict[str, Any]) -> None:
        """Update a specific attribute based on register data."""
        register_id = data_item["id"]
        value = data_item["value"]

        # Store raw register value
        self.registers[register_id] = value

        register_map = {
            RegisterConstants.REG_MAINBOARD_USERMODE_MODE_HMI: ("user_mode", value),
            RegisterConstants.REG_MAINBOARD_SPEED_INDICATION_APP: ("airflow", value),
            RegisterConstants.REG_MAINBOARD_TC_SP: ("temperatures", ("setpoint", value / 10.0)),
            RegisterConstants.REG_MAINBOARD_USERMODE_REMAINING_TIME_L: ("user_mode_remaining_time", value),
            RegisterConstants.REG_MAINBOARD_USERMODE_HOLIDAY_TIME: ("user_mode_times", ("holiday", value)),
            RegisterConstants.REG_MAINBOARD_USERMODE_AWAY_TIME: ("user_mode_times", ("away", value)),
            RegisterConstants.REG_MAINBOARD_USERMODE_FIREPLACE_TIME: ("user_mode_times", ("fireplace", value)),
            RegisterConstants.REG_MAINBOARD_USERMODE_REFRESH_TIME: ("user_mode_times", ("refresh", value)),
            RegisterConstants.REG_MAINBOARD_USERMODE_CROWDED_TIME: ("user_mode_times", ("crowded", value)),
            RegisterConstants.REG_MAINBOARD_IAQ_LEVEL: ("air_quality", value),
            RegisterConstants.REG_MAINBOARD_SENSOR_OAT: ("temperatures", ("oat", value / 10.0)),
            RegisterConstants.REG_MAINBOARD_ECO_MODE_ON_OFF: ("eco_mode", value),
            RegisterConstants.REG_MAINBOARD_LOCKED_USER: ("locked_user", value),
            RegisterConstants.REG_MAINBOARD_ALARM_TYPE_A: ("alarm_type_a", value),
            RegisterConstants.REG_MAINBOARD_ALARM_TYPE_B: ("alarm_type_b", value),
            RegisterConstants.REG_MAINBOARD_ALARM_TYPE_C: ("alarm_type_c", value),
            RegisterConstants.REG_MAINBOARD_SUW_REQUIRED: ("suw_required", value),
            RegisterConstants.REG_MAINBOARD_UNIT_CONFIG_REHEATER_TYPE: ("reheater_type", value),
        }

        if register_id in register_map:
            attr, val = register_map[register_id]
            if attr == "temperatures":
                key, temp_val = val
                self.temperatures[key] = temp_val
            elif attr == "user_mode_times":
                key, time_val = val
                self.user_mode_times[key] = time_val
            else:
                setattr(self, attr, val)
        elif register_id in range(
            RegisterConstants.REG_MAINBOARD_FUNCTION_ACTIVE_COOLING, RegisterConstants.REG_MAINBOARD_FUNCTION_ACTIVE_CDI_3 + 1
        ):
            function_name = RegisterConstants.get_register_name(register_id).split("_")[-1].lower()
            self.active_functions[function_name] = value

    def update_from_websocket(self, ws_data: dict[str, Any]) -> None:
        """Update the ventilation unit with data from a WebSocket message."""
        properties = ws_data.get("properties", ws_data)

        # Map simple properties directly
        simple_props = {
            "model": "model",
            "activeAlarms": "active_alarms",
            "airflow": "airflow",
            "connectivity": "connectivity",
            "filterExpiration": "filter_expiration",
            "serialNumber": "serial_number",
            "temperature": "temperature",
            "userMode": "user_mode",
            "airQuality": "air_quality",
            "humidity": "humidity",
            "co2": "co2",
        }

        for json_key, attr_name in simple_props.items():
            if json_key in properties:
                setattr(self, attr_name, properties[json_key])

        # Update nested properties
        if "update" in properties:
            self.update_in_progress = properties["update"].get("inProgress", self.update_in_progress)

        if "configurationWizard" in properties:
            self.configuration_wizard_active = properties["configurationWizard"].get("active", self.configuration_wizard_active)

        # Update temperature data
        if "temperatures" in properties:
            for key, value in properties["temperatures"].items():
                if key in self.temperatures:
                    self.temperatures[key] = value

        # Update version data
        if "versions" in properties:
            self.versions = properties["versions"]

    def __str__(self) -> str:
        """Return string representation of the ventilation unit."""
        return f"VentilationUnit: {self.name} (ID: {self.identifier})"

    @property
    def user_mode_name(self) -> str:
        """Get the name of the current user mode."""
        if self.user_mode is None:
            return "Unknown"
        return VentilationData.get_user_mode_name(self.user_mode)

    def get_fan_speed(self) -> int:
        """Get the fan speed as a percentage (0-100)."""
        return self.airflow or 0

    def get_filter_alarm(self) -> bool:
        """Check if there's a filter alarm active."""
        # Placeholder implementation - will need to be updated based on how filter alarms are detected
        return self.active_alarms

    def get_status(self) -> dict[str, Any]:
        """Get the current status of the ventilation unit as a dictionary."""
        return {
            "name": self.name,
            "model": self.model,
            "active_alarms": self.active_alarms,
            "airflow": self.airflow,
            "connectivity": self.connectivity,
            "filter_expiration": self.filter_expiration,
            "serial_number": self.serial_number,
            "temperature": self.temperature,
            "user_mode": self.user_mode,
            "user_mode_name": self.user_mode_name,
            "air_quality": self.air_quality,
            "humidity": self.humidity,
            "co2": self.co2,
            "update_in_progress": self.update_in_progress,
            "configuration_wizard_active": self.configuration_wizard_active,
            "temperatures": self.temperatures,
            "versions": self.versions,
            "eco_mode": self.eco_mode,
            "locked_user": self.locked_user,
            "alarm_type_a": self.alarm_type_a,
            "alarm_type_b": self.alarm_type_b,
            "alarm_type_c": self.alarm_type_c,
            "suw_required": self.suw_required,
            "reheater_type": self.reheater_type,
            "active_functions": self.active_functions,
            "user_mode_remaining_time": self.user_mode_remaining_time,
            "user_mode_times": self.user_mode_times,
        }

    def set_value(self, api: SystemairAPI, key: int, value: float | str, *, _noprint: bool = False) -> bool | None:
        """
        Set a register value for the ventilation unit.

        Args:
            api: The SystemairAPI instance to use for communication
            key: The register key to set
            value: The value to set
            _noprint: Whether to suppress print output

        Returns:
            bool: True if successful, False otherwise

        """
        result = api.write_data_item(self.identifier, key, value)
        return bool(result and result.get("data", {}).get("WriteDataItems"))

    def set_user_mode(self, api: SystemairAPI, mode_value: int, time_minutes: int | None = None) -> None:
        """
        Set the user mode for the ventilation unit.

        Args:
            api: The SystemairAPI instance to use for communication
            mode_value: The mode value to set (use UserModes enum)
            time_minutes: Optional time duration in minutes for timed modes
                (Refresh, Crowded, Fireplace, Away, Holiday)

        Returns:
            None

        """
        # Map mode values to their time registers and determine if we need to set time
        mode_to_time_register = {
            UserModes.HOLIDAY: RegisterConstants.REG_MAINBOARD_USERMODE_HOLIDAY_TIME,
            UserModes.AWAY: RegisterConstants.REG_MAINBOARD_USERMODE_AWAY_TIME,
            UserModes.FIREPLACE: RegisterConstants.REG_MAINBOARD_USERMODE_FIREPLACE_TIME,
            UserModes.REFRESH: RegisterConstants.REG_MAINBOARD_USERMODE_REFRESH_TIME,
            UserModes.CROWDED: RegisterConstants.REG_MAINBOARD_USERMODE_CROWDED_TIME,
        }

        # Set the time value first if provided and this is a timed mode
        time_register = mode_to_time_register.get(mode_value)
        if time_minutes is not None and time_register is not None:
            # Convert minutes to the units expected by each specific register
            api_time_value = self._convert_minutes_to_api_units(mode_value, time_minutes)
            self.set_value(api, time_register, api_time_value, _noprint=True)
            # Update local cache (keep in minutes for internal use)
            mode_key = self.get_mode_name_for_key(mode_value)
            if mode_key and hasattr(self, "user_mode_times") and mode_key in self.user_mode_times:
                self.user_mode_times[mode_key] = time_minutes

        # Then set the mode
        self.set_value(api, RegisterConstants.REG_MAINBOARD_USERMODE_HMI_CHANGE_REQUEST, mode_value + 1, _noprint=True)

    def _convert_minutes_to_api_units(self, mode_value: int, time_minutes: int) -> int:
        """
        Convert time in minutes to the units expected by the API for each mode.

        API expects:
        - HOLIDAY: days (REG_MAINBOARD_USERMODE_HOLIDAY_TIME = 251)
        - AWAY: hours (REG_MAINBOARD_USERMODE_AWAY_TIME = 252)
        - FIREPLACE: minutes (REG_MAINBOARD_USERMODE_FIREPLACE_TIME = 253)
        - REFRESH: minutes (REG_MAINBOARD_USERMODE_REFRESH_TIME = 254)
        - CROWDED: hours (REG_MAINBOARD_USERMODE_CROWDED_TIME = 255)
        """
        if mode_value == UserModes.HOLIDAY:
            return max(1, time_minutes // (24 * 60))  # Convert to days, minimum 1
        if mode_value in [UserModes.AWAY, UserModes.CROWDED]:
            return max(1, time_minutes // 60)  # Convert to hours, minimum 1
        if mode_value in [UserModes.FIREPLACE, UserModes.REFRESH]:
            return time_minutes  # Already in minutes
        return time_minutes  # Fallback

    def get_mode_name_for_key(self, mode_value: int) -> str:
        """
        Map numeric mode value to string mode key.

        Args:
            mode_value: The numeric mode value from UserModes enum

        Returns:
            str: The string key name (e.g., 'holiday', 'away', etc.)

        """
        mode_map = {
            UserModes.HOLIDAY: "holiday",
            UserModes.AWAY: "away",
            UserModes.FIREPLACE: "fireplace",
            UserModes.REFRESH: "refresh",
            UserModes.CROWDED: "crowded",
        }
        return mode_map.get(mode_value, "")

    def set_temperature(self, api: SystemairAPI, temperature: int) -> None:
        """
        Set the temperature setpoint for the ventilation unit.

        Args:
            api: The SystemairAPI instance to use for communication
            temperature: Temperature in tenths of degrees (e.g., 210 for 21.0°C)

        Returns:
            None

        """
        self.set_value(api, RegisterConstants.REG_MAINBOARD_TC_SP, temperature, _noprint=True)

    def set_user_mode_time(self, api: SystemairAPI, mode: str, time_value: int) -> None:
        """
        Set the time duration for a specific user mode.

        Args:
            api: The SystemairAPI instance to use for communication
            mode: The mode to set time for ('holiday', 'away', 'fireplace', 'refresh', 'crowded')
            time_value: The time duration in minutes

        Returns:
            None

        """
        # Map mode names to their respective registers and mode values
        mode_info = {
            "holiday": (RegisterConstants.REG_MAINBOARD_USERMODE_HOLIDAY_TIME, UserModes.HOLIDAY),
            "away": (RegisterConstants.REG_MAINBOARD_USERMODE_AWAY_TIME, UserModes.AWAY),
            "fireplace": (RegisterConstants.REG_MAINBOARD_USERMODE_FIREPLACE_TIME, UserModes.FIREPLACE),
            "refresh": (RegisterConstants.REG_MAINBOARD_USERMODE_REFRESH_TIME, UserModes.REFRESH),
            "crowded": (RegisterConstants.REG_MAINBOARD_USERMODE_CROWDED_TIME, UserModes.CROWDED),
        }

        if mode not in mode_info:
            return

        register, mode_value = mode_info[mode]

        # Convert minutes to the units expected by the API for this specific mode
        api_time_value = self._convert_minutes_to_api_units(mode_value, time_value)

        if self.set_value(api, register, api_time_value, _noprint=True):
            # Update our local cache (keep in minutes for internal consistency)
            self.user_mode_times[mode] = time_value

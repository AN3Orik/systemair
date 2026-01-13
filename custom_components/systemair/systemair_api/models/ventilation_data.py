"""Ventilation data constants and definitions."""

USER_MODES: dict[int, dict[str, str]] = {
    0: {
        "name": "Auto",
        "description": "Takes care of airflow levels automatically",
        "info": (
            "AUTO mode is available to select if Demand Control or Week Schedule functions are configured and/or airflow "
            'type is selected "External". Demand Control shall control the airflow to ensure the best possible air quality '
            "with respect to RH and/or CO2 sensor readings."
        ),
    },
    1: {
        "name": "Manual",
        "description": "Set the airflow levels manually",
        "info": (
            "The airflow levels are controlled manually. The unit can be set to run on one out of four available airflow levels: "
            "OFF/LOW/NORMAL/HIGH."
        ),
    },
    2: {
        "name": "Crowded",
        "description": "When you have extra guests",
        "info": (
            "Crowded function increases the airflow to level HIGH and reduces the temperature setpoint to ensure a perfect indoor "
            "climate when there are guests. The delay is in hours."
        ),
    },
    3: {
        "name": "Refresh",
        "description": "Quick change of air",
        "info": (
            "The airflow levels are increased to HIGH to replace the indoor air with fresh air in a short period of time. "
            "Function duration in minutes."
        ),
    },
    4: {
        "name": "Fireplace",
        "description": "Start your fire without smoke inside",
        "info": (
            "The airflow levels are regulated so that a slight overpressure is created indoors (Supply air fan - NORMAL, "
            "Extract air fan - LOW) for better smoke extraction through the chimney. Function duration can be set in minutes."
        ),
    },
    5: {
        "name": "Away",
        "description": "Save energy while being away",
        "info": (
            "To save energy when You are away from home for a short period of time, the airflow levels are reduced to LOW and "
            "the ECO mode function is activated. The function duration can be set in hours, default duration - 10 hours."
        ),
    },
    6: {
        "name": "Holiday",
        "description": "Saves energy while You are on Holidays",
        "info": (
            "To save energy when You are on Holidays the airflow levels are reduced to LOW and the ECO mode is activated. "
            "The function duration can be set in Days, default duration - 16 Days."
        ),
    },
}

AIRFLOW_LEVELS: dict[int, str] = {
    0: "Off",
    1: "Minimum",
    2: "Low",
    3: "Normal",
    4: "High",
    5: "Maximum",
    6: "Demand",
    7: "External",
}


class VentilationData:
    """Data definitions for ventilation units."""

    @staticmethod
    def get_user_mode_name(mode_id: int) -> str:
        """Get the name of a user mode by ID."""
        return USER_MODES.get(mode_id, {}).get("name", "Unknown")

    @staticmethod
    def get_airflow_level_name(level_id: int) -> str:
        """Get the name of an airflow level by ID."""
        return AIRFLOW_LEVELS.get(level_id, "Unknown")

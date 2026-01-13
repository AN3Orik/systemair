#!/usr/bin/env python
"""Main entry point for the systemair_api package."""

import logging
import os
import time

from dotenv import load_dotenv

from .api.systemair_api import SystemairAPI
from .api.websocket_client import SystemairWebSocket
from .auth.authenticator import SystemairAuthenticator
from .models.ventilation_unit import VentilationUnit
from .utils.constants import UserModes

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
_LOGGER = logging.getLogger(__name__)


def on_message(message: dict) -> None:
    """
    Handle incoming WebSocket messages.

    Args:
        message: The message received from the WebSocket

    """
    _LOGGER.info("Received WebSocket message: %s", message)


def _setup_api() -> tuple[SystemairAPI, str] | None:
    """Authenticate and create API client."""
    # Load environment variables from .env file if it exists
    load_dotenv()

    # Get credentials from environment variables
    email = os.getenv("EMAIL")
    password = os.getenv("PASSWORD")

    if not email or not password:
        _LOGGER.error("Please set EMAIL and PASSWORD environment variables")
        _LOGGER.error("You can create a .env file with these variables")
        return None

    # Authenticate
    authenticator = SystemairAuthenticator(email, password)
    access_token = authenticator.authenticate()

    if not access_token:
        _LOGGER.error("Authentication failed")
        return None

    _LOGGER.info("Authentication successful, access token obtained")
    return SystemairAPI(access_token), access_token


def _get_devices(api: SystemairAPI) -> list[VentilationUnit]:
    """Fetch and return ventilation units."""
    devices_response = api.get_account_devices()
    if not devices_response or "data" not in devices_response:
        _LOGGER.error("Failed to get devices")
        return []

    devices = devices_response["data"]["GetAccountDevices"]
    if not devices:
        _LOGGER.info("No devices found")
        return []

    _LOGGER.info("Found %d devices:", len(devices))
    ventilation_units = []

    for device in devices:
        _LOGGER.info(" - %s (ID: %s)", device["name"], device["identifier"])
        ventilation_unit = VentilationUnit(device["identifier"], device["name"])
        ventilation_units.append(ventilation_unit)

    return ventilation_units


def _run_demo(api: SystemairAPI, unit: VentilationUnit) -> None:
    """Run a demo sequence on the unit."""
    # Get device status
    status_response = api.fetch_device_status(unit.identifier)
    if status_response:
        unit.update_from_api(status_response)
        _LOGGER.info("\nCurrent Status for %s:", unit.name)
        _LOGGER.info(unit.get_status())

        # Broadcast to get updates via WebSocket
        api.broadcast_device_statuses([unit.identifier])

        # Example: Change user mode to Away
        _LOGGER.info("\nChanging user mode to Away...")
        unit.set_user_mode(api, UserModes.AWAY)

        # Wait for a moment to receive WebSocket updates
        time.sleep(5)

        # Change user mode back to Auto
        _LOGGER.info("\nChanging user mode back to Auto...")
        unit.set_user_mode(api, UserModes.AUTO)

        # Get updated status
        status_response = api.fetch_device_status(unit.identifier)
        if status_response:
            unit.update_from_api(status_response)
            _LOGGER.info("\nUpdated Status:")
            _LOGGER.info(unit.get_status())


def main() -> None:
    """Run the example application demonstrating the SystemAIR API."""
    setup_result = _setup_api()
    if not setup_result:
        return

    api, access_token = setup_result
    ventilation_units = _get_devices(api)

    # Set up WebSocket client
    ws_client = SystemairWebSocket(access_token, on_message)
    ws_client.connect()

    try:
        # Get status for the first device
        if ventilation_units:
            _run_demo(api, ventilation_units[0])

        # Keep the main thread alive for WebSocket messages
        _LOGGER.info("\nListening for WebSocket messages. Press Ctrl+C to exit.")
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        _LOGGER.info("\nExiting...")
    finally:
        # Disconnect WebSocket
        ws_client.disconnect()


if __name__ == "__main__":
    main()

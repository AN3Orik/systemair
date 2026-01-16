"""SystemairWebSocket - WebSocket client for real-time updates from Systemair ventilation units."""

import json
import logging
import ssl
import threading
from collections.abc import Callable
from typing import Any

import websocket
from websocket import WebSocket, WebSocketApp

from custom_components.systemair.systemair_api.utils.constants import WEBSOCKET_URL

_LOGGER = logging.getLogger(__name__)


class SystemairWebSocket:
    """
    WebSocket client for real-time updates from Systemair Home Solutions API.

    Establishes a persistent connection to the Systemair WebSocket server
    and processes incoming messages through a callback function.
    """

    def __init__(self, access_token: str, on_message_callback: Callable[[dict[str, Any]], None]) -> None:
        """
        Initialize the WebSocket client.

        Args:
            access_token: A valid JWT access token from authentication
            on_message_callback: Callback function that will be called with message data

        """
        self.access_token: str = access_token
        self.on_message_callback: Callable[[dict[str, Any]], None] = on_message_callback
        self.ws: WebSocketApp | None = None
        self.thread: threading.Thread | None = None

    def on_message(self, _ws: WebSocket, message: Any) -> None:
        """
        Handle incoming WebSocket messages.

        Args:
            _ws: WebSocket connection
            message: Raw message data

        """
        data = json.loads(message)
        self.on_message_callback(data)

    def on_error(self, _ws: WebSocket, error: Any) -> None:
        """
        Handle WebSocket errors.

        Args:
            _ws: WebSocket connection
            error: Error information

        """
        # Log to stdout for diagnostic purposes, but keep it minimal
        _LOGGER.error("WebSocket error: %s", error)

    def on_close(self, _ws: WebSocket, close_status_code: Any, _close_msg: Any) -> None:
        """
        Handle WebSocket connection closure.

        Args:
            _ws: WebSocket connection
            close_status_code: Status code for the closure
            _close_msg: Closure message

        """
        # Important status messages are kept to help diagnose issues
        if close_status_code:
            _LOGGER.info("WebSocket connection closed with code: %s", close_status_code)
        else:
            _LOGGER.info("WebSocket connection closed")

    def on_open(self, _ws: WebSocket) -> None:
        """
        Handle WebSocket connection opening.

        Args:
            _ws: WebSocket connection

        """
        # Connection established notification is useful for debugging
        _LOGGER.info("WebSocket connection opened")

    def connect(self) -> None:
        """
        Establish a WebSocket connection in a separate thread.

        The connection is opened in a daemon thread to allow the main program
        to continue execution.
        """
        # Disable WebSocket trace output to keep logs cleaner
        websocket.enableTrace(traceable=False)
        self.ws = websocket.WebSocketApp(
            WEBSOCKET_URL,
            header=[
                f"Sec-WebSocket-Protocol: accessToken, {self.access_token}",
                "Origin: https://homesolutions.systemair.com",
            ],
            on_open=self.on_open,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close,
        )
        self.thread = threading.Thread(target=self.ws.run_forever, kwargs={"sslopt": {"cert_reqs": ssl.CERT_NONE}})
        self.thread.daemon = True
        self.thread.start()

    def disconnect(self) -> None:
        """Close the WebSocket connection and clean up resources."""
        if self.ws:
            self.ws.close()
        if self.thread:
            self.thread.join()

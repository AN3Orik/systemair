"""SystemairAPI - Core API communication module for Systemair ventilation units."""

from http import HTTPStatus
from typing import Any, cast

import requests

from custom_components.systemair.systemair_api.utils.constants import APIEndpoints
from custom_components.systemair.systemair_api.utils.exceptions import (
    APIError,
    DeviceNotFoundError,
    DeviceOfflineError,
    RateLimitError,
    ValidationError,
)

# HTTP status code constant for server errors
HTTP_STATUS_SERVER_ERROR = 500


class SystemairAPI:
    """
    Core API interface for communicating with Systemair Home Solutions API.

    Provides methods for discovering devices, fetching device status,
    and sending control commands to ventilation units.
    """

    def __init__(self, access_token: str) -> None:
        """
        Initialize the SystemairAPI with an access token.

        Args:
            access_token: A valid JWT access token from authentication

        """
        self.access_token: str = access_token
        self.headers: dict[str, str] = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:128.0) Gecko/20100101 Firefox/128.0",
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Referer": "https://homesolutions.systemair.com/device/home",
            "content-type": "application/json",
            "x-access-token": self.access_token,
            "Origin": "https://homesolutions.systemair.com",
            "Connection": "keep-alive",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
        }

    def update_token(self, access_token: str) -> None:
        """
        Update the access token used for API requests.

        This method should be called when the token is refreshed.

        Args:
            access_token: The new access token

        """
        self.access_token = access_token
        self.headers["x-access-token"] = access_token

    def broadcast_device_statuses(self, device_ids: list[str]) -> dict[str, Any]:
        """
        Broadcast requests for device statuses to trigger WebSocket updates.

        Args:
            device_ids: List of device identifiers to request updates for

        Returns:
            dict: API response

        Raises:
            APIError: If the API request fails
            DeviceNotFoundError: If one or more devices are not found
            RateLimitError: If rate limit is exceeded

        """
        data = {
            "variables": {"deviceIds": device_ids},
            "query": """
            query ($deviceIds: [String]!) {
                BroadcastDeviceStatuses(deviceIds: $deviceIds)
            }
            """,
        }

        try:
            response = requests.post(APIEndpoints.GATEWAY, headers=self.headers, json=data, timeout=10)
        except requests.exceptions.RequestException as e:
            status_code = getattr(e, "response", None) and getattr(e.response, "status_code", None)
            msg = f"Failed to broadcast device statuses: {e!s}"
            raise APIError(msg, status_code) from e

        if response.status_code == HTTPStatus.TOO_MANY_REQUESTS:
            retry_after = response.headers.get("Retry-After")
            retry_seconds = int(retry_after) if retry_after and retry_after.isdigit() else None
            raise RateLimitError(retry_after=retry_seconds)

        response.raise_for_status()
        result = cast("dict[str, Any]", response.json())

        # Check for error in response data
        if "errors" in result:
            errors = result["errors"]
            for error in errors:
                if "message" in error and any(device_id in error.get("message", "") for device_id in device_ids):
                    raise DeviceNotFoundError(device_ids[0], error.get("message"))
            raise APIError(message=errors[0].get("message", "Unknown API error"), response_data=result)

        return result

    def fetch_device_status(self, device_id: str) -> dict[str, Any]:
        """
        Fetch detailed status for a specific device.

        Args:
            device_id: The unique identifier of the device

        Returns:
            dict: API response with detailed device status

        Raises:
            APIError: If the API request fails
            DeviceNotFoundError: If the device is not found
            RateLimitError: If rate limit is exceeded

        """
        headers = self.headers.copy()
        headers["device-id"] = device_id
        headers["device-type"] = "LEGACY"

        data = {
            "variables": {"input": {"route": "/home", "viewId": ""}},
            "query": """
            query ($input: GetViewInputType!) {
                GetView(input: $input) {
                    children {
                        type
                        properties
                    }
                }
            }
            """,
        }

        try:
            response = requests.post(APIEndpoints.REMOTE, headers=headers, json=data, timeout=10)
        except requests.exceptions.RequestException as e:
            status_code = getattr(e, "response", None) and getattr(e.response, "status_code", None)
            if status_code == HTTPStatus.NOT_FOUND:
                raise DeviceNotFoundError(device_id, str(e)) from e
            msg = f"Failed to fetch device status: {e!s}"
            raise APIError(msg, status_code) from e

        if response.status_code == HTTPStatus.NOT_FOUND:
            raise DeviceNotFoundError(device_id)

        if response.status_code == HTTPStatus.TOO_MANY_REQUESTS:
            retry_after = response.headers.get("Retry-After")
            retry_seconds = int(retry_after) if retry_after and retry_after.isdigit() else None
            raise RateLimitError(retry_after=retry_seconds)

        if response.status_code >= HTTP_STATUS_SERVER_ERROR:
            # Check if it's a DeviceOfflineError wrapped in a 500 response
            try:
                error_data = response.json()
                if error_data.get("name") == "DeviceOfflineError":
                    raise DeviceOfflineError(device_id, error_data.get("msg"))
            except (ValueError, AttributeError):
                pass  # Not JSON or not the expected structure

        response.raise_for_status()
        result = cast("dict[str, Any]", response.json())

        # Check for error in response data
        if "errors" in result:
            errors = result["errors"]
            for error in errors:
                if "message" in error and device_id in error.get("message", ""):
                    raise DeviceNotFoundError(device_id, error.get("message"))
            raise APIError(message=errors[0].get("message", "Unknown API error"), response_data=result)

        return result

    def get_account_devices(self) -> dict[str, Any]:
        """
        Get all devices associated with the current account.

        Returns:
            dict: API response with devices list

        Raises:
            APIError: If the API request fails
            RateLimitError: If rate limit is exceeded

        """
        data = {
            "operationName": "GetLoggedInAccount",
            "variables": {},
            "query": """
            query GetLoggedInAccount {
              GetAccountDevices {
                identifier
                name
                street
                zipcode
                city
                country
                deviceType {
                  entry
                  module
                  scope
                  type
                }
              }
            }
            """,
        }

        try:
            response = requests.post(APIEndpoints.GATEWAY, headers=self.headers, json=data, timeout=10)
        except requests.exceptions.RequestException as e:
            status_code = getattr(e, "response", None) and getattr(e.response, "status_code", None)
            msg = f"Failed to fetch account devices: {e!s}"
            raise APIError(msg, status_code) from e

        if response.status_code == HTTPStatus.TOO_MANY_REQUESTS:
            retry_after = response.headers.get("Retry-After")
            retry_seconds = int(retry_after) if retry_after and retry_after.isdigit() else None
            raise RateLimitError(retry_after=retry_seconds)

        response.raise_for_status()
        result = cast("dict[str, Any]", response.json())

        # Check for error in response data
        if "errors" in result:
            errors = result["errors"]
            raise APIError(message=errors[0].get("message", "Unknown API error"), response_data=result, status_code=response.status_code)

        return result

    def write_data_item(self, device_id: str, register_id: int, value: float | str) -> dict[str, Any]:
        """
        Write a value to a specific register on a device.

        Args:
            device_id: The unique identifier of the device
            register_id: The register ID to write to
            value: The value to write

        Returns:
            dict: API response indicating success

        Raises:
            APIError: If the API request fails
            DeviceNotFoundError: If the device is not found
            RateLimitError: If rate limit is exceeded
            ValidationError: If the provided value is invalid

        """
        headers = self.headers.copy()
        headers["device-id"] = device_id
        headers["device-type"] = "LEGACY"

        data = {
            "variables": {"input": {"dataPoints": [{"id": register_id, "value": str(value)}]}},
            "query": """
            mutation ($input: WriteDataItemsInput!) {
                WriteDataItems(input: $input)
            }
            """,
        }

        try:
            response = requests.post(APIEndpoints.REMOTE, headers=headers, json=data, timeout=10)
        except requests.exceptions.RequestException as e:
            status_code = getattr(e, "response", None) and getattr(e.response, "status_code", None)
            if status_code == HTTPStatus.NOT_FOUND:
                raise DeviceNotFoundError(device_id, str(e)) from e
            msg = f"Failed to write data to device: {e!s}"
            raise APIError(msg, status_code) from e

        if response.status_code == HTTPStatus.NOT_FOUND:
            raise DeviceNotFoundError(device_id)

        if response.status_code == HTTPStatus.TOO_MANY_REQUESTS:
            retry_after = response.headers.get("Retry-After")
            retry_seconds = int(retry_after) if retry_after and retry_after.isdigit() else None
            raise RateLimitError(retry_after=retry_seconds)

        response.raise_for_status()
        result = cast("dict[str, Any]", response.json())

        # Check for error in response data
        if "errors" in result:
            errors = result["errors"]
            for error in errors:
                msg = error.get("message", "")
                if "device" in msg.lower() and "not found" in msg.lower():
                    raise DeviceNotFoundError(device_id, msg)
                if "invalid" in msg.lower() or "validation" in msg.lower():
                    raise ValidationError(message=msg, field=f"register_{register_id}", value=value)
            raise APIError(message=errors[0].get("message", "Unknown API error"), response_data=result)

        return result

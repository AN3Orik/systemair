"""SystemairAPI - Core API communication module for Systemair ventilation units."""

from dataclasses import dataclass
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


@dataclass(frozen=True)
class HomeSolutionViewsResponse:
    """Results from one aliased HomeSolution GetView request."""

    views: dict[str, dict[str, Any] | None]
    errors: dict[str, str]


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

    @staticmethod
    def _raise_for_status(response: requests.Response, message: str, device_id: str | None = None) -> None:
        """Translate HTTP failures into the bundled API exception hierarchy."""
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as err:
            try:
                response_data = response.json()
            except (ValueError, TypeError):
                response_data = None
            if device_id is not None and isinstance(response_data, dict) and response_data.get("name") == "DeviceOfflineError":
                raise DeviceOfflineError(device_id, response_data.get("msg")) from err
            raise APIError(message, response.status_code, response_data if isinstance(response_data, dict) else None) from err

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

        self._raise_for_status(response, "Failed to broadcast device statuses")
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

        self._raise_for_status(response, "Failed to fetch device status", device_id)
        result = cast("dict[str, Any]", response.json())

        # Check for error in response data
        if "errors" in result:
            errors = result["errors"]
            for error in errors:
                if "message" in error and device_id in error.get("message", ""):
                    raise DeviceNotFoundError(device_id, error.get("message"))
            raise APIError(message=errors[0].get("message", "Unknown API error"), response_data=result)

        return result

    def fetch_device_views(self, device_id: str, routes: tuple[str, ...]) -> HomeSolutionViewsResponse:
        """Fetch multiple device views in a single aliased GraphQL request."""
        if not routes:
            return HomeSolutionViewsResponse(views={}, errors={})

        headers = self.headers.copy()
        headers["device-id"] = device_id
        headers["device-type"] = "LEGACY"
        variable_definitions: list[str] = []
        fields: list[str] = []
        variables: dict[str, dict[str, str]] = {}
        alias_to_route: dict[str, str] = {}
        for index, route in enumerate(routes):
            variable = f"i{index}"
            alias = f"v{index}"
            variable_definitions.append(f"${variable}: GetViewInputType!")
            fields.append(f"{alias}: GetView(input: ${variable}) {{ children {{ type properties }} }}")
            variables[variable] = {"route": route, "viewId": ""}
            alias_to_route[alias] = route

        query = f"query ({', '.join(variable_definitions)}) {{ {' '.join(fields)} }}"
        try:
            response = requests.post(
                APIEndpoints.REMOTE,
                headers=headers,
                json={"query": query, "variables": variables},
                timeout=20,
            )
        except requests.exceptions.RequestException as err:
            status_code = getattr(err, "response", None) and getattr(err.response, "status_code", None)
            msg = f"Failed to fetch device views: {err!s}"
            raise APIError(msg, status_code) from err

        if response.status_code == HTTPStatus.TOO_MANY_REQUESTS:
            retry_after = response.headers.get("Retry-After")
            retry_seconds = int(retry_after) if retry_after and retry_after.isdigit() else None
            raise RateLimitError(retry_after=retry_seconds)

        self._raise_for_status(response, "Failed to fetch device views", device_id)
        result = cast("dict[str, Any]", response.json())
        response_data = result.get("data") or {}
        views = {route: response_data.get(alias) for alias, route in alias_to_route.items()}
        errors: dict[str, str] = {}
        for error in result.get("errors", []):
            path = error.get("path") or []
            if path and (route := alias_to_route.get(str(path[0]))) is not None:
                errors[route] = error.get("message", "Unknown API error")

        return HomeSolutionViewsResponse(views=views, errors=errors)

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

        self._raise_for_status(response, "Failed to fetch account devices")
        result = cast("dict[str, Any]", response.json())

        # Check for error in response data
        if "errors" in result:
            errors = result["errors"]
            raise APIError(message=errors[0].get("message", "Unknown API error"), response_data=result, status_code=response.status_code)

        return result

    def write_data_item(self, device_id: str, register_id: int, value: float | str) -> dict[str, Any]:
        """Write one data item to a device."""
        return self.write_data_items(device_id, ((register_id, value),))

    def write_data_items(
        self,
        device_id: str,
        data_points: tuple[tuple[int, float | str], ...],
    ) -> dict[str, Any]:
        """
        Write one or more values to a device in a single mutation.

        Args:
            device_id: The unique identifier of the device
            data_points: Register IDs and values to write

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
            "variables": {"input": {"dataPoints": [{"id": register_id, "value": str(value)} for register_id, value in data_points]}},
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

        self._raise_for_status(response, "Failed to write data to device", device_id)
        result = cast("dict[str, Any]", response.json())

        # Check for error in response data
        if "errors" in result:
            errors = result["errors"]
            for error in errors:
                msg = error.get("message", "")
                if "device" in msg.lower() and "not found" in msg.lower():
                    raise DeviceNotFoundError(device_id, msg)
                if "invalid" in msg.lower() or "validation" in msg.lower():
                    raise ValidationError(message=msg, field="data_points", value=data_points)
            raise APIError(message=errors[0].get("message", "Unknown API error"), response_data=result)

        return result

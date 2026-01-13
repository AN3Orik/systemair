"""Exception classes for the SystemAIR API."""

from typing import Any


class SystemairError(Exception):
    """Base exception for all SystemAIR API related errors."""

    def __init__(self, message: str, *args: Any) -> None:
        """
        Initialize the exception.

        Args:
            message: The error message
            *args: Additional arguments to pass to the parent class

        """
        self.message = message
        super().__init__(message, *args)


class AuthenticationError(SystemairError):
    """Exception raised for authentication failures."""

    def __init__(self, message: str = "Authentication failed", *args: Any) -> None:
        """
        Initialize the exception.

        Args:
            message: The error message
            *args: Additional arguments to pass to the parent class

        """
        super().__init__(message, *args)


class TokenRefreshError(AuthenticationError):
    """Exception raised when token refresh fails."""

    def __init__(self, message: str = "Failed to refresh access token", *args: Any) -> None:
        """
        Initialize the exception.

        Args:
            message: The error message
            *args: Additional arguments to pass to the parent class

        """
        super().__init__(message, *args)


class AuthPageStructureError(AuthenticationError):
    """Exception raised when the login page structure has changed."""

    def __init__(self, message: str = "Login page structure changed", *args: Any) -> None:
        """
        Initialize the exception.

        Args:
            message: The error message
            *args: Additional arguments to pass to the parent class

        """
        super().__init__(message, *args)


class APIError(SystemairError):
    """Exception raised for all API related errors."""

    def __init__(
        self,
        message: str = "API request failed",
        status_code: int | None = None,
        response_data: dict[str, Any] | None = None,
        *args: Any,
    ) -> None:
        """
        Initialize the exception.

        Args:
            message: The error message
            status_code: The HTTP status code
            response_data: The response data from the API
            *args: Additional arguments to pass to the parent class

        """
        self.status_code = status_code
        self.response_data = response_data
        if status_code:
            message = f"{message} (status code: {status_code})"
        super().__init__(message, *args)


class DeviceNotFoundError(APIError):
    """Exception raised when a device is not found."""

    def __init__(self, device_id: str, message: str | None = None, *args: Any) -> None:
        """
        Initialize the exception.

        Args:
            device_id: The ID of the device that was not found
            message: The error message
            *args: Additional arguments to pass to the parent class

        """
        self.device_id = device_id
        if message is None:
            message = f"Device with ID {device_id} not found"
        super().__init__(message, None, None, *args)


class DeviceOfflineError(APIError):
    """Exception raised when a device is offline."""

    def __init__(self, device_id: str, message: str | None = None, *args: Any) -> None:
        """
        Initialize the exception.

        Args:
            device_id: The ID of the device that is offline
            message: The error message
            *args: Additional arguments to pass to the parent class

        """
        self.device_id = device_id
        if message is None:
            message = f"Device with ID {device_id} is offline"
        super().__init__(message, None, None, *args)


class WebSocketError(SystemairError):
    """Exception raised for WebSocket related errors."""

    def __init__(self, message: str = "WebSocket connection error", *args: Any) -> None:
        """
        Initialize the exception.

        Args:
            message: The error message
            *args: Additional arguments to pass to the parent class

        """
        super().__init__(message, *args)


class RateLimitError(APIError):
    """Exception raised when rate limits are exceeded."""

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: int | None = None,
        *args: Any,
    ) -> None:
        """
        Initialize the exception.

        Args:
            message: The error message
            retry_after: The number of seconds to wait before retrying
            *args: Additional arguments to pass to the parent class

        """
        self.retry_after = retry_after
        if retry_after:
            message = f"{message}. Retry after {retry_after} seconds."
        super().__init__(message, 429, None, *args)


class ValidationError(SystemairError):
    """Exception raised for validation errors."""

    def __init__(
        self,
        message: str = "Validation error",
        field: str | None = None,
        value: Any | None = None,
        *args: Any,
    ) -> None:
        """
        Initialize the exception.

        Args:
            message: The error message
            field: The field that failed validation
            value: The value that failed validation
            *args: Additional arguments to pass to the parent class

        """
        self.field = field
        self.value = value
        if field and value is not None:
            message = f"{message}: {field}={value}"
        elif field:
            message = f"{message}: {field}"
        super().__init__(message, *args)

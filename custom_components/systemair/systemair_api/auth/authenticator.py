"""SystemairAuthenticator - Authentication module for Systemair Home Solutions cloud."""

import base64
import json
import logging
import uuid
from datetime import datetime, timedelta
from http import HTTPStatus
from typing import TYPE_CHECKING, Any, cast

import requests
from bs4 import BeautifulSoup

from custom_components.systemair.systemair_api.utils.constants import CLIENT_ID, REDIRECT_URI, APIEndpoints

if TYPE_CHECKING:
    from bs4.element import Tag
from custom_components.systemair.systemair_api.utils.exceptions import AuthenticationError, AuthPageStructureError, TokenRefreshError

_LOGGER = logging.getLogger(__name__)


class SystemairAuthenticator:
    """
    Authentication handler for Systemair Home Solutions cloud.

    Manages the OAuth2 authentication flow, including:
    - Initial login with username/password
    - Token exchange
    - Token refresh
    - Token validation
    """

    def __init__(self, email: str, password: str) -> None:
        """
        Initialize the authenticator with user credentials.

        Args:
            email: User's email address
            password: User's password

        """
        self.email: str = email
        self.password: str = password
        self.session: requests.Session = requests.Session()
        self.access_token: str | None = None
        self.refresh_token: str | None = None
        self.token_expiry: datetime | None = None

    def generate_state_parameter(self) -> str:
        """
        Generate a random state parameter for the OAuth flow.

        Returns:
            str: A random UUID as string

        """
        return str(uuid.uuid4())

    def construct_auth_url(self, state: str) -> str:
        """
        Construct the OAuth authorization URL.

        Args:
            state: State parameter to include in the URL

        Returns:
            str: Complete authorization URL

        """
        params = {"client_id": CLIENT_ID, "response_type": "code", "state": state, "redirect_uri": REDIRECT_URI, "scope": "openid"}
        query_string = "&".join([f"{key}={value}" for key, value in params.items()])
        return f"{APIEndpoints.AUTH}?{query_string}"

    def _get_login_page_content(self, auth_url: str) -> bytes:
        _LOGGER.debug("Fetching login page from: %s", auth_url)
        try:
            response = self.session.get(auth_url, timeout=10)
        except requests.RequestException as err:
            msg = f"Network error fetching login page: {err}"
            raise AuthenticationError(msg) from err

        response.raise_for_status()
        return response.content

    def _extract_login_form_data(self, content: bytes) -> tuple[str, dict[str, str]]:
        soup = BeautifulSoup(content, "html.parser")
        form = soup.find("form")
        if not form:
            _LOGGER.error("Login form not found in the response")
            msg = "Login form not found - Systemair login page structure might have changed"
            raise AuthPageStructureError(msg)

        form_tag = cast("Tag", form)
        if not form_tag.has_attr("action"):
            _LOGGER.error("Action attribute not found in login form")
            msg = "Action attribute not found in login form"
            raise AuthPageStructureError(msg)

        action_url = form_tag["action"]
        # Handle potential list type for action_url by ensuring it's a string
        action_url_str = (action_url[0] if action_url else "") if isinstance(action_url, list) else str(action_url)

        inputs = form_tag.find_all("input")
        form_data = {}
        for input_tag in inputs:
            input_tag = cast("Tag", input_tag)
            name = input_tag.get("name")
            if name == "username":
                form_data[name] = self.email
            elif name == "password":
                form_data[name] = self.password
            elif name:
                form_data[name] = input_tag.get("value", "")
        return action_url_str, form_data

    def _submit_login_form(self, action_url: str, form_data: dict[str, str]) -> requests.Response:
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:128.0) Gecko/20100101 Firefox/128.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/png,image/svg+xml,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        _LOGGER.debug("Submitting login form to %s", action_url)
        try:
            return self.session.post(action_url, data=form_data, headers=headers, allow_redirects=False, timeout=10)
        except requests.RequestException as err:
            msg = f"Network error submitting login form: {err}"
            raise AuthenticationError(msg) from err

    def _handle_login_redirect(self, response: requests.Response) -> str:
        redirect_url = response.headers.get("Location")
        if redirect_url is None:
            msg = "Redirect URL not found in headers"
            raise AuthenticationError(msg)

        try:
            response = self.session.get(redirect_url, allow_redirects=True, timeout=10)
        except requests.RequestException as err:
            msg = f"Network error following redirect: {err}"
            raise AuthenticationError(msg) from err

        _LOGGER.debug("Redirect follow-up response status: %s %s", response.status_code, response.reason)

        if response.status_code == HTTPStatus.OK:
            if "code=" in response.url:
                auth_code = response.url.split("code=")[1].split("&")[0]
                _LOGGER.info("Authentication code obtained successfully")
                return auth_code
            _LOGGER.error("Authorization code not found in final URL: %s", response.url)
            msg = "Authorization code not found in final URL"
            raise AuthenticationError(msg)
        msg = f"Failed to follow redirect URL. Status: {response.status_code}"
        raise AuthenticationError(msg)

    def simulate_login(self, auth_url: str) -> str:
        """
        Simulate a browser login to obtain the authorization code.

        This method simulates the browser login process by:
        1. Fetching the login page
        2. Extracting the form and input fields
        3. Submitting the form with credentials
        4. Following redirects to obtain the authorization code

        Args:
            auth_url: The authorization URL to start the flow

        Returns:
            str: The authorization code if successful

        Raises:
            AuthenticationError: If login fails
            AuthPageStructureError: If the page structure has changed

        """
        content = self._get_login_page_content(auth_url)
        action_url, form_data = self._extract_login_form_data(content)
        response = self._submit_login_form(action_url, form_data)

        _LOGGER.debug("Login form submission response status: %s %s", response.status_code, response.reason)

        if response.status_code == HTTPStatus.FOUND:
            return self._handle_login_redirect(response)

        _LOGGER.error("Login failed. Status: %s, Reason: %s", response.status_code, response.reason)
        msg = "Login failed or redirect did not occur"
        raise AuthenticationError(msg)

    def exchange_code_for_token(self, auth_code: str) -> dict[str, Any]:
        """
        Exchange an authorization code for access and refresh tokens.

        Args:
            auth_code: The authorization code obtained from login

        Returns:
            dict: Token response containing access_token, refresh_token, etc.

        Raises:
            AuthenticationError: If token exchange fails

        """
        data = {
            "grant_type": "authorization_code",
            "code": auth_code,
            "redirect_uri": REDIRECT_URI,
            "client_id": CLIENT_ID,
        }
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:128.0) Gecko/20100101 Firefox/128.0",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Content-Type": "application/x-www-form-urlencoded;charset=utf-8",
            "Origin": "https://homesolutions.systemair.com",
            "Connection": "keep-alive",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "TE": "trailers",
        }

        _LOGGER.debug("Exchanging authorization code for token")
        try:
            response = requests.post(APIEndpoints.TOKEN, data=data, headers=headers, timeout=10)
        except requests.RequestException as err:
            msg = f"Network error exchanging code for token: {err}"
            raise AuthenticationError(msg) from err

        if response.status_code == HTTPStatus.OK:
            return cast("dict[str, Any]", response.json())
        _LOGGER.error("Failed to exchange code for token. Status: %s, Response: %s", response.status_code, response.content)
        msg = f"Failed to exchange code for token: {response.status_code} - {response.text}"
        raise AuthenticationError(msg)

    def authenticate(self) -> str:
        """
        Perform the full authentication flow.

        This method orchestrates the complete authentication process:
        1. Generate state parameter
        2. Construct auth URL
        3. Simulate login to get authorization code
        4. Exchange code for tokens
        5. Extract token expiry time

        Returns:
            str: The access token if successful

        Raises:
            AuthenticationError: If authentication fails for any reason

        """
        state = self.generate_state_parameter()
        auth_url = self.construct_auth_url(state)
        auth_code = self.simulate_login(auth_url)
        token_response = self.exchange_code_for_token(auth_code)
        self.access_token = token_response.get("access_token")
        self.refresh_token = token_response.get("refresh_token")

        if not self.access_token:
            msg = "No access token found in response"
            raise AuthenticationError(msg)

        self.token_expiry = self.get_token_expiry(self.access_token)
        return str(self.access_token)

    def refresh_access_token(self) -> str:
        """
        Refresh the access token using the refresh token.

        Returns:
            str: The new access token if successful

        Raises:
            TokenRefreshError: If refresh fails or no refresh token is available

        """
        if not self.refresh_token:
            msg = "No refresh token available. Please authenticate first."
            raise TokenRefreshError(msg)

        data = {
            "grant_type": "refresh_token",
            "client_id": CLIENT_ID,
            "refresh_token": self.refresh_token,
            "redirect_uri": REDIRECT_URI,
        }
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:128.0) Gecko/20100101 Firefox/128.0",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Content-Type": "application/x-www-form-urlencoded;charset=utf-8",
            "Origin": "https://homesolutions.systemair.com",
            "Connection": "keep-alive",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
        }

        _LOGGER.debug("Refreshing access token")
        try:
            response = requests.post(APIEndpoints.TOKEN, data=data, headers=headers, timeout=10)
        except requests.RequestException as err:
            msg = f"Network error refreshing token: {err}"
            raise TokenRefreshError(msg) from err

        if response.status_code == HTTPStatus.OK:
            token_data = response.json()
            self.access_token = token_data.get("access_token")
            self.refresh_token = token_data.get("refresh_token")  # Update refresh token if provided

            if not self.access_token:
                _LOGGER.error("No access token found in refresh response")
                msg = "No access token found in refresh response"
                raise TokenRefreshError(msg)

            self.token_expiry = self.get_token_expiry(self.access_token)
            _LOGGER.info("Access token refreshed successfully")
            return str(self.access_token)
        _LOGGER.error("Failed to refresh token. Status: %s, Response: %s", response.status_code, response.text)
        msg = f"Failed to refresh token: {response.status_code} - {response.text}"
        raise TokenRefreshError(msg)

    def _decode_token_expiry(self, token: str) -> datetime:
        # Split the token and get the payload part (second part)
        payload = token.split(".")[1]

        # Add padding if necessary
        payload += "=" * ((4 - len(payload) % 4) % 4)

        # Decode the Base64 string
        decoded_payload = base64.b64decode(payload)

        # Parse the JSON
        token_data = json.loads(decoded_payload)

        # Extract the expiry time
        exp_timestamp = token_data.get("exp")

        if exp_timestamp:
            # Use timezone-aware datetime for UTC
            return datetime.fromtimestamp(exp_timestamp, tz=datetime.now().astimezone().tzinfo)
        msg = "No expiry time found in token"
        raise ValueError(msg)

    def get_token_expiry(self, token: str) -> datetime | None:
        """
        Decode the JWT and extract the expiry time.

        Args:
            token: JWT token to decode

        Returns:
            datetime: Token expiry time as datetime object

        """
        try:
            return self._decode_token_expiry(token)
        except (ValueError, TypeError, json.JSONDecodeError):
            return None

    def is_token_valid(self) -> bool:
        """
        Check if the current token is still valid.

        Returns:
            bool: True if token is valid, False otherwise

        """
        if not self.token_expiry:
            return False

        # Consider the token invalid if it's about to expire in the next 30 seconds
        return datetime.now(tz=datetime.now().astimezone().tzinfo) + timedelta(seconds=30) < self.token_expiry

import json

from config import BASE_URI
from services.serverest_api.serverest_client import ServeRestClient


class Login(ServeRestClient):
    """ServeRest client wrapper for login endpoint."""

    def __init__(self):
        """Configure base URL for login operations."""
        super().__init__()
        self.login_url = f"{BASE_URI}/login"

    def login(self, payload):
        """POST credentials and return the API response."""
        url = f"{self.login_url}"
        return self.request.post_request(url, json.dumps(payload), self.headers)

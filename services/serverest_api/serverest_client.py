from services.base_client import BaseClient
from utils.request import APIRequest


class ServeRestClient(BaseClient):
    """Base wrapper that wires ServeRest-specific request helpers."""

    def __init__(self):
        """Set up the shared API request helper."""
        super().__init__()
        self.request = APIRequest()

    # TODO: Add test after implemented
    def get_service_status(self):
        """Placeholder for a future health-check call."""
        pass

class BaseClient:
    """Provide shared headers for ServeRest API clients."""

    def __init__(self):
        """Populate default headers used by child clients."""
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        self.headers_with_token = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": "",
        }

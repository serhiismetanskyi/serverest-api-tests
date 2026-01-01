from dataclasses import dataclass

import requests

from utils.logger import Logger


@dataclass
class APIResponse:
    """Lightweight container for HTTP response data."""

    status_code: int
    text: str
    as_dict: object
    headers: dict


class APIRequest:
    """Wrapper around requests with logging and unified responses."""

    def get_request(self, url, headers):
        """Execute a GET request."""
        Logger.add_request(url, method="GET", headers=headers)
        response = requests.get(url=url, headers=headers)
        Logger.add_response(response)
        return self.get_responses(response)

    def post_request(self, url, payload, headers):
        """Execute a POST request."""
        Logger.add_request(url, method="POST", body=payload, headers=headers)
        response = requests.post(url=url, data=payload, headers=headers)
        Logger.add_response(response)
        return self.get_responses(response)

    def put_request(self, url, payload, headers):
        """Execute a PUT request."""
        Logger.add_request(url, method="PUT", body=payload, headers=headers)
        response = requests.put(url=url, data=payload, headers=headers)
        Logger.add_response(response)
        return self.get_responses(response)

    def delete_request(self, url, headers):
        """Execute a DELETE request."""
        Logger.add_request(url, method="DELETE", headers=headers)
        response = requests.delete(url=url, data=None, headers=headers)
        Logger.add_response(response)
        return self.get_responses(response)

    @staticmethod
    def get_responses(response):
        """Convert a raw response into APIResponse."""
        status_code = response.status_code
        text = response.text
        try:
            as_dict = response.json()
        except ValueError:
            as_dict = {}
        headers = response.headers
        return APIResponse(status_code, text, as_dict, headers)

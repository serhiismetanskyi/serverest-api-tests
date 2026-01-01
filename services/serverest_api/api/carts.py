import json

from config import BASE_URI
from services.serverest_api.serverest_client import ServeRestClient


class Carts(ServeRestClient):
    """ServeRest client wrapper for cart endpoints."""

    def __init__(self):
        """Configure base URL for cart operations."""
        super().__init__()
        self.carts_url = f"{BASE_URI}/carrinhos"

    def create_cart(self, payload, token):
        """POST a cart using the provided token."""
        url = f"{self.carts_url}"
        self.headers_with_token["Authorization"] = token
        return self.request.post_request(url, json.dumps(payload), self.headers_with_token)

    def get_carts(self, **kwargs):
        """GET carts with optional filters."""
        url_params = {key: value for key, value in kwargs.items() if value is not None}
        url = f"{self.carts_url}?"
        url += "&".join([f"{key}={value}" for key, value in url_params.items()])
        return self.request.get_request(url, self.headers)

    def get_cart_by_id(self, cart_id):
        """GET a cart by id."""
        url = f"{self.carts_url}/{cart_id}"
        return self.request.get_request(url, self.headers)

    def checkout(self, token):
        """DELETE the user's cart via checkout endpoint."""
        url = f"{self.carts_url}/concluir-compra"
        self.headers_with_token["Authorization"] = token
        return self.request.delete_request(url, self.headers_with_token)

    def delete_cart(self, token):
        """DELETE the user's cart via cancel endpoint."""
        url = f"{self.carts_url}/cancelar-compra"
        self.headers_with_token["Authorization"] = token
        return self.request.delete_request(url, self.headers_with_token)

"""Shared pytest fixtures and helpers for ServeRest API tests."""

import random

import pytest

from config import (
    MAX_CARTS_COUNT,
    MAX_PRODUCTS_COUNT,
    MAX_PRODUCTS_PER_CART_COUNT,
    MAX_QUANTITY_PER_PRODUCT,
    MAX_USERS_COUNT,
)
from services.serverest_api.api.carts import Carts
from services.serverest_api.api.login import Login
from services.serverest_api.api.products import Products
from services.serverest_api.api.users import Users
from utils.calculator import Calculator
from utils.data_generator import DataGenerator
from utils.file_manager import FileManager


def pytest_configure(config):
    """Pytest configuration hook."""
    pass


@pytest.fixture
def context():
    """Return a mutable dict used to share data between fixtures."""
    return {}


@pytest.fixture
def get_user_token(context):
    """Return a helper that fetches user tokens from the shared context."""
    users_list = context.get("usuarios")

    def get_token(user_id):
        """Return the stored token for the given user id."""
        if not users_list:
            raise ValueError("No users found in context. Ensure create_user fixture runs first.")
        user = next((user for user in users_list if user["_id"] == user_id), None)
        if user:
            authorization = user.get("authorization")
            if not authorization:
                raise ValueError(
                    f"User with id {user_id} is missing authorization token. Ensure login_user fixture runs first."
                )
            return authorization
        else:
            raise ValueError(f"User with id {user_id} not found")

    return get_token


@pytest.fixture
def random_admin_token(context):
    """Return a random admin token from users stored in context."""
    users_list = context.get("usuarios")
    if not users_list:
        raise ValueError("No users found in context. Ensure create_user fixture runs before create_product.")

    admins = [user for user in users_list if user["administrador"] == "true"]
    if not admins:
        raise ValueError("No admin users found. Ensure at least one admin user is created.")

    random_admin = random.choice(admins)
    authorization = random_admin.get("authorization")
    if not authorization:
        raise ValueError(
            "Admin user missing authorization token. Ensure login_user fixture runs before create_product."
        )

    return authorization


@pytest.fixture
def get_product_ids(context):
    """Return product ids saved in context."""
    product_ids = context.get("produto_ids")
    if not product_ids:
        raise ValueError("No products found in context. Ensure create_product fixture runs first.")
    return product_ids


@pytest.fixture
def get_product_price(context):
    """Return a helper that exposes product prices from context."""
    products_list = context.get("produtos")

    def get_price(product_id):
        """Return stored price for the given product id."""
        if not products_list:
            raise ValueError("No products available. Ensure create_product fixture runs first.")
        product = next((product for product in products_list if product["_id"] == product_id), None)
        if product:
            return product["preco"]
        else:
            raise ValueError(f"Product with id {product_id} not found")

    return get_price


@pytest.fixture
def get_products_quantity(context):
    """Return mapping of product ids to available quantities."""
    products = context.get("produtos")
    if not products:
        raise ValueError("No products found in context. Ensure create_product fixture runs first.")
    quantity_map = {product["_id"]: product["quantidade"] for product in products}
    return quantity_map


@pytest.fixture
def user_data_for_create():
    """Generate user payloads for create scenarios and load from disk."""
    DataGenerator.generate_user_data_for_create(num_users=MAX_USERS_COUNT)
    return FileManager.read_file("create_user_data.json")


@pytest.fixture
def user_data_for_update():
    """Generate user payloads for update scenarios and load from disk."""
    DataGenerator.generate_user_data_for_update(num_users=MAX_USERS_COUNT)
    return FileManager.read_file("update_user_data.json")


@pytest.fixture
def create_user(user_data_for_create, context):
    """Create users via API and persist them in the shared context."""
    client = Users()
    users = user_data_for_create["usuarios"]
    responses = []

    # Create each user and store response data
    for user_data in users:
        response = client.create_user(user_data)
        responses.append(response)

        # Verify response has _id before storing
        if not response.as_dict or "_id" not in response.as_dict:
            raise ValueError(f"Failed to create user: {response.as_dict}")

        # Add the generated ID to user data for later use
        user_data["_id"] = response.as_dict["_id"]

    # Store created users in shared context
    context.update({"usuarios": users})

    return responses


@pytest.fixture
def login_user(create_user, context):
    """Log created users in and attach tokens to the shared context."""
    client = Login()
    users = context.get("usuarios")
    responses = []

    # Login each user and store authorization token
    for user_data in users:
        login_data = {"email": user_data.get("email"), "password": user_data.get("password")}

        if not login_data["email"] or not login_data["password"]:
            raise ValueError(f"User data missing email or password: {user_data}")

        response = client.login(login_data)
        responses.append(response)

        # Verify response has authorization token before storing
        if not response.as_dict or "authorization" not in response.as_dict:
            raise ValueError(f"Failed to login user {login_data['email']}: {response.as_dict}")

        # Store authorization token in user data
        user_data["authorization"] = response.as_dict["authorization"]

    # Update context with users containing authorization tokens
    context["usuarios"] = users

    return responses


@pytest.fixture
def product_data_for_create():
    """Generate product creation data and load it from disk."""
    DataGenerator.generate_product_data_for_create(num_products=MAX_PRODUCTS_COUNT)
    return FileManager.read_file("create_product_data.json")


@pytest.fixture
def product_data_for_update():
    """Generate product update data and load it from disk."""
    DataGenerator.generate_product_data_for_update(num_products=MAX_PRODUCTS_COUNT)
    return FileManager.read_file("update_product_data.json")


@pytest.fixture
def create_product(login_user, random_admin_token, product_data_for_create, context):
    """Create products with admin token and capture ids in context."""
    client = Products()
    token = random_admin_token
    products = product_data_for_create["produtos"]
    product_ids = []
    responses = []

    # Create each product and store response data
    for product_data in products:
        response = client.create_product(product_data, token)
        responses.append(response)

        # Verify response has _id before storing
        if not response.as_dict or "_id" not in response.as_dict:
            raise ValueError(f"Failed to create product: {response.as_dict}")

        # Add the generated ID to product data and collect IDs
        product_data["_id"] = response.as_dict["_id"]
        product_ids.append(response.as_dict["_id"])

    # Store created products and IDs in shared context
    context.update({"produto_ids": product_ids, "produtos": products})

    return responses


@pytest.fixture
def generate_cart_data_for_create(get_product_ids, get_products_quantity):
    """Build cart payloads based on generated products and inventory."""
    DataGenerator.generate_cart_data_for_create(
        get_product_ids,
        get_products_quantity,
        num_carts=MAX_CARTS_COUNT,
        max_products_per_cart=MAX_PRODUCTS_PER_CART_COUNT,
        max_quantity_per_product=MAX_QUANTITY_PER_PRODUCT,
    )
    return FileManager.read_file("create_cart_data.json")


@pytest.fixture
def create_cart(
    login_user,
    create_product,
    generate_cart_data_for_create,
    context,
    get_product_price,
):
    """Create carts for every user and enrich context with totals."""
    client = Carts()
    users = context.get("usuarios")

    if not users:
        raise ValueError("No users found in context. Ensure login_user fixture runs before create_cart.")

    carts = generate_cart_data_for_create["carrinhos"]
    responses = []

    # Create cart for each user
    for user_data, cart_data in zip(users, carts, strict=False):
        user_id = user_data["_id"]
        token = user_data.get("authorization")

        if not token:
            raise ValueError(
                f"User {user_id} is missing authorization token. Ensure login_user fixture runs before create_cart."
            )

        # Create the cart
        response = client.create_cart(cart_data, token)
        responses.append(response)

        # Verify response has _id before storing
        if not response.as_dict or "_id" not in response.as_dict:
            raise ValueError(f"Failed to create cart for user {user_id}: {response.as_dict}")

        # Add generated cart ID to cart data
        cart_data["_id"] = response.as_dict["_id"]

        # Calculate total quantity and price for validation
        products = cart_data["produtos"]
        quantity_total = Calculator.calculate_quantity_total_in_cart(products)
        price_total = 0

        # Calculate total price for all products in cart
        for product in products:
            _id = product["idProduto"]
            quantity = product["quantidade"]
            price = get_product_price(_id)
            price_total += Calculator.calculate_price_total_in_cart(price, quantity)

        # Store calculated values and user ID in cart data
        cart_data["quantidadeTotal"] = quantity_total
        cart_data["precoTotal"] = price_total
        cart_data["idUsuario"] = user_id

    # Store created carts in shared context
    context.update({"carrinhos": carts})

    return responses

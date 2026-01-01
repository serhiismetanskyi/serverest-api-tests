"""
Configuration module for ServeRest API tests.

This module handles environment variable configuration and provides
default values for various test parameters. It uses python-dotenv
to load configuration from .env files.
"""

import os

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Configuration
BASE_URI = os.getenv("BASE_URI", "https://serverest.dev")

# Test Data Limits Configuration
# These values control how many test entities are created during test execution
MAX_USERS_COUNT = int(os.getenv("MAX_USERS_COUNT", "3"))
MAX_PRODUCTS_COUNT = int(os.getenv("MAX_PRODUCTS_COUNT", "6"))
MAX_CARTS_COUNT = int(os.getenv("MAX_CARTS_COUNT", "3"))

# Cart Configuration
# These values control cart creation behavior
MAX_PRODUCTS_PER_CART_COUNT = int(os.getenv("MAX_PRODUCTS_PER_CART_COUNT", "3"))
MAX_QUANTITY_PER_PRODUCT = int(os.getenv("MAX_QUANTITY_PER_PRODUCT", "3"))

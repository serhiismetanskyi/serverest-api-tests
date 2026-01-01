"""Tests for ServeRest carts endpoints."""

import logging

from assertpy import assert_that, soft_assertions

from services.serverest_api.api.carts import Carts

logger = logging.getLogger(__name__)


class TestCarts:
    """High-level cart scenarios covering CRUD, lookup, and checkout."""

    client = Carts()

    def test_if_cart_can_be_created(self, login_user, create_cart, context):
        """Ensure carts can be created and return expected payload."""
        logger.info("Starting test: test_if_cart_can_be_created")
        responses = create_cart
        logger.info(f"Created {len(responses)} cart(s)")

        with soft_assertions():
            for idx, response in enumerate(responses):
                logger.info(f"Verifying cart {idx + 1} creation response")
                # Verify successful creation status code
                assert_that(response.status_code).is_equal_to(201)
                logger.debug(f"Cart {idx + 1} - Status code: {response.status_code}")

                # Verify response contains data
                assert_that(response.as_dict).is_not_empty()
                logger.debug(f"Cart {idx + 1} - Response data: {response.as_dict}")

                # Verify success message
                assert_that(response.as_dict["message"]).contains("Cadastro realizado com sucesso")
                logger.debug(f"Cart {idx + 1} - Success message verified")

                # Verify cart ID is present and not null
                assert_that(response.as_dict).contains("_id")
                assert_that(response.as_dict["_id"]).is_not_none()
                logger.info(f"Cart {idx + 1} created successfully with ID: {response.as_dict['_id']}")

        logger.info("Test completed: test_if_cart_can_be_created")

    def test_if_cart_can_be_fetched(self, login_user, create_cart, context, get_product_price):
        """Assert filtered cart queries return matching data."""
        logger.info("Starting test: test_if_cart_can_be_fetched")
        carts = context.get("carrinhos")

        if not carts:
            logger.error("No carts found in context")
            raise ValueError("No carts found in context")

        logger.info(f"Fetching {len(carts)} cart(s) with filters")
        with soft_assertions():
            for idx, cart_data in enumerate(carts):
                # Extract cart data for filtering
                _id = cart_data["_id"]
                price_total = cart_data["precoTotal"]
                quantity_total = cart_data["quantidadeTotal"]
                user_id = cart_data["idUsuario"]
                logger.info(f"Fetching cart {idx + 1} - ID: {_id}, User ID: {user_id}, Total Price: {price_total}")

                # Retrieve cart with filter parameters
                response = self.client.get_carts(
                    _id=_id,
                    precoTotal=price_total,
                    quantidadeTotal=quantity_total,
                    idUsuario=user_id,
                )

                # Verify successful retrieval
                assert_that(response.status_code).is_equal_to(200)
                logger.debug(f"Cart {idx + 1} - Status code: {response.status_code}")
                assert_that(response.as_dict).is_not_empty()

                # Verify returned cart data matches created data
                assert_that(response.as_dict).contains("carrinhos")
                for cart in response.as_dict.get("carrinhos", []):
                    assert_that(cart).contains_key(
                        "_id",
                        "precoTotal",
                        "quantidadeTotal",
                        "idUsuario",
                        "produtos",
                    )
                    assert_that(cart["_id"]).is_equal_to(_id)
                    assert_that(cart["precoTotal"]).is_equal_to(price_total)
                    assert_that(cart["quantidadeTotal"]).is_equal_to(quantity_total)
                    assert_that(cart["idUsuario"]).is_equal_to(user_id)

                    # Verify product details in cart
                    for product in cart.get("produtos", []):
                        product_id = product["idProduto"]
                        product_price = get_product_price(product_id)
                        product_quantity = product["quantidade"]

                        assert_that(product["idProduto"]).is_equal_to(product_id)
                        assert_that(product["precoUnitario"]).is_equal_to(product_price)
                        assert_that(product["quantidade"]).is_equal_to(product_quantity)
                logger.info(f"Cart {idx + 1} fetched and verified successfully")

        logger.info("Test completed: test_if_cart_can_be_fetched")

    def test_if_cart_can_be_fetched_by_id(
        self,
        login_user,
        create_cart,
        context,
        get_product_price,
    ):
        """Verify cart detail endpoint mirrors stored context data."""
        logger.info("Starting test: test_if_cart_can_be_fetched_by_id")
        carts = context.get("carrinhos")

        if not carts:
            logger.error("No carts found in context")
            raise ValueError("No carts found in context")

        logger.info(f"Fetching {len(carts)} cart(s) by ID")
        with soft_assertions():
            for idx, cart_data in enumerate(carts):
                # Extract cart data for verification
                _id = cart_data["_id"]
                price_total = cart_data["precoTotal"]
                quantity_total = cart_data["quantidadeTotal"]
                user_id = cart_data["idUsuario"]
                logger.info(f"Fetching cart {idx + 1} by ID: {_id}")

                # Retrieve cart by ID
                response = self.client.get_cart_by_id(_id)

                # Verify successful retrieval
                assert_that(response.status_code).is_equal_to(200)
                logger.debug(f"Cart {idx + 1} - Status code: {response.status_code}")
                assert_that(response.as_dict).is_not_empty()

                # Verify returned cart data matches created data
                assert_that(response.as_dict).contains_key(
                    "_id",
                    "precoTotal",
                    "quantidadeTotal",
                    "idUsuario",
                    "produtos",
                )
                assert_that(response.as_dict["_id"]).is_equal_to(_id)
                assert_that(response.as_dict["precoTotal"]).is_equal_to(price_total)
                assert_that(response.as_dict["quantidadeTotal"]).is_equal_to(quantity_total)
                assert_that(response.as_dict["idUsuario"]).is_equal_to(user_id)

                # Verify product details in cart
                for product in response.as_dict.get("produtos", []):
                    product_id = product["idProduto"]
                    product_price = get_product_price(product_id)
                    product_quantity = product["quantidade"]

                    assert_that(product["idProduto"]).is_equal_to(product_id)
                    assert_that(product["precoUnitario"]).is_equal_to(product_price)
                    assert_that(product["quantidade"]).is_equal_to(product_quantity)
                logger.info(f"Cart {idx + 1} fetched by ID and verified successfully")

        logger.info("Test completed: test_if_cart_can_be_fetched_by_id")

    def test_if_cart_can_be_checkout(self, login_user, create_cart, context, get_user_token):
        """Confirm checkout completes successfully for every cart."""
        logger.info("Starting test: test_if_cart_can_be_checkout")
        carts = context.get("carrinhos")

        if not carts:
            logger.error("No carts found in context")
            raise ValueError("No carts found in context")

        logger.info(f"Processing checkout for {len(carts)} cart(s)")
        with soft_assertions():
            for idx, cart_data in enumerate(carts):
                user_id = cart_data["idUsuario"]
                token = get_user_token(user_id)
                logger.info(f"Processing checkout for cart {idx + 1} - User ID: {user_id}")

                # Perform checkout operation
                response = self.client.checkout(token)

                # Verify successful checkout
                assert_that(response.status_code).is_equal_to(200)
                logger.debug(f"Cart {idx + 1} - Status code: {response.status_code}")
                assert_that(response.as_dict).is_not_empty()
                assert_that(response.as_dict["message"]).contains("Registro excluído com sucesso")
                logger.info(f"Cart {idx + 1} checkout completed successfully")

        logger.info("Test completed: test_if_cart_can_be_checkout")

    def test_if_cart_can_be_deleted(self, login_user, create_cart, context, get_user_token):
        """Ensure cart deletion works and stock adjustments succeed."""
        logger.info("Starting test: test_if_cart_can_be_deleted")
        carts = context.get("carrinhos")

        if not carts:
            logger.error("No carts found in context")
            raise ValueError("No carts found in context")

        logger.info(f"Deleting {len(carts)} cart(s)")
        with soft_assertions():
            for idx, cart_data in enumerate(carts):
                user_id = cart_data["idUsuario"]
                token = get_user_token(user_id)
                logger.info(f"Deleting cart {idx + 1} - User ID: {user_id}")

                # Delete cart (cancel purchase)
                response = self.client.delete_cart(token)

                # Verify successful deletion
                assert_that(response.status_code).is_equal_to(200)
                logger.debug(f"Cart {idx + 1} - Status code: {response.status_code}")
                assert_that(response.as_dict).is_not_empty()
                assert_that(response.as_dict["message"]).contains(
                    "Registro excluído com sucesso. Estoque dos produtos reabastecido"
                )
                logger.info(f"Cart {idx + 1} deleted successfully")

        logger.info("Test completed: test_if_cart_can_be_deleted")

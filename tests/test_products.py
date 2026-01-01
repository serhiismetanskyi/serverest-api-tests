"""Tests for ServeRest products endpoints."""

import logging

from assertpy import assert_that, soft_assertions

from services.serverest_api.api.products import Products

logger = logging.getLogger(__name__)


class TestProducts:
    """Covers CRUD flows for products."""

    client = Products()

    def test_if_product_can_be_created(self, login_user, create_product, context):
        """Ensure product creation requests succeed."""
        logger.info("Starting test: test_if_product_can_be_created")
        responses = create_product
        logger.info(f"Created {len(responses)} product(s)")

        with soft_assertions():
            for idx, response in enumerate(responses):
                logger.info(f"Verifying product {idx + 1} creation response")
                # Verify successful creation status code
                assert_that(response.status_code).is_equal_to(201)
                logger.debug(f"Product {idx + 1} - Status code: {response.status_code}")

                # Verify response contains data
                assert_that(response.as_dict).is_not_empty()
                logger.debug(f"Product {idx + 1} - Response data: {response.as_dict}")

                # Verify success message
                assert_that(response.as_dict["message"]).contains("Cadastro realizado com sucesso")
                logger.debug(f"Product {idx + 1} - Success message verified")

                # Verify product ID is present and not null
                assert_that(response.as_dict).contains("_id")
                assert_that(response.as_dict["_id"]).is_not_none()
                logger.info(f"Product {idx + 1} created successfully with ID: {response.as_dict['_id']}")

        logger.info("Test completed: test_if_product_can_be_created")

    def test_if_product_can_be_fetched(self, login_user, create_product, context):
        """Check filtered searches return the expected products."""
        logger.info("Starting test: test_if_product_can_be_fetched")
        products = context.get("produtos")

        if not products:
            logger.error("No products found in context")
            raise ValueError("No products found in context")

        logger.info(f"Fetching {len(products)} product(s) with filters")
        with soft_assertions():
            for idx, product_data in enumerate(products):
                # Extract product data for filtering
                _id = product_data["_id"]
                name = product_data["nome"]
                price = product_data["preco"]
                description = product_data["descricao"]
                quantity = product_data["quantidade"]
                logger.info(f"Fetching product {idx + 1} - ID: {_id}, Name: {name}, Price: {price}")

                # Retrieve product with filter parameters
                response = self.client.get_product(
                    _id=_id,
                    nome=name,
                    preco=price,
                    descricao=description,
                    quantidade=quantity,
                )

                # Verify successful retrieval
                assert_that(response.status_code).is_equal_to(200)
                logger.debug(f"Product {idx + 1} - Status code: {response.status_code}")
                assert_that(response.as_dict).is_not_empty()

                # Verify returned product data matches created data
                assert_that(response.as_dict).contains("produtos")
                for product in response.as_dict.get("produtos", []):
                    assert_that(product["nome"]).is_equal_to(name)
                    assert_that(product["preco"]).is_equal_to(price)
                    assert_that(product["descricao"]).is_equal_to(description)
                    assert_that(product["quantidade"]).is_equal_to(quantity)
                logger.info(f"Product {idx + 1} fetched and verified successfully")

        logger.info("Test completed: test_if_product_can_be_fetched")

    def test_if_product_can_be_fetched_by_id(self, login_user, create_product, context):
        """Validate detail lookup matches stored context."""
        logger.info("Starting test: test_if_product_can_be_fetched_by_id")
        products = context.get("produtos")

        if not products:
            logger.error("No products found in context")
            raise ValueError("No products found in context")

        logger.info(f"Fetching {len(products)} product(s) by ID")
        with soft_assertions():
            for idx, product_data in enumerate(products):
                # Extract product data for verification
                _id = product_data["_id"]
                name = product_data["nome"]
                price = product_data["preco"]
                description = product_data["descricao"]
                quantity = product_data["quantidade"]
                logger.info(f"Fetching product {idx + 1} by ID: {_id}")

                # Retrieve product by ID
                response = self.client.get_product_by_id(_id)

                # Verify successful retrieval
                assert_that(response.status_code).is_equal_to(200)
                logger.debug(f"Product {idx + 1} - Status code: {response.status_code}")
                assert_that(response.as_dict).is_not_empty()

                # Verify returned product data matches created data
                assert_that(response.as_dict).contains_key(
                    "_id",
                    "nome",
                    "preco",
                    "descricao",
                    "quantidade",
                )
                assert_that(response.as_dict["_id"]).is_equal_to(_id)
                assert_that(response.as_dict["nome"]).is_equal_to(name)
                assert_that(response.as_dict["preco"]).is_equal_to(price)
                assert_that(response.as_dict["descricao"]).is_equal_to(description)
                assert_that(response.as_dict["quantidade"]).is_equal_to(quantity)
                logger.info(f"Product {idx + 1} fetched by ID and verified successfully")

        logger.info("Test completed: test_if_product_can_be_fetched_by_id")

    def test_if_product_can_be_updated(
        self,
        login_user,
        random_admin_token,
        create_product,
        context,
        product_data_for_update,
    ):
        """Confirm updates succeed when using admin token."""
        logger.info("Starting test: test_if_product_can_be_updated")
        token = random_admin_token
        products = context.get("produtos")

        if not products:
            logger.error("No products found in context")
            raise ValueError("No products found in context")

        logger.info(f"Updating {len(products)} product(s)")
        with soft_assertions():
            for index, product_data in enumerate(products):
                _id = product_data["_id"]
                logger.info(f"Updating product {index + 1} with ID: {_id}")

                # Validate update data availability
                if not product_data_for_update or "produtos" not in product_data_for_update:
                    logger.error("Product data for update not found")
                    raise ValueError("Product data for update not found")
                if index >= len(product_data_for_update["produtos"]):
                    logger.error(f"Update data not available for product index {index}")
                    raise ValueError(f"Update data not available for product index {index}")

                update_data = product_data_for_update["produtos"][index]
                logger.debug(f"Product {index + 1} - Update data: {update_data}")

                # Update product with new data using admin token
                response = self.client.update_product(_id, update_data, token)

                # Verify successful update
                assert_that(response.status_code).is_equal_to(200)
                logger.debug(f"Product {index + 1} - Status code: {response.status_code}")
                assert_that(response.as_dict).is_not_empty()
                assert_that(response.as_dict["message"]).contains("Registro alterado com sucesso")
                logger.info(f"Product {index + 1} updated successfully")

                # Update local product data for consistency
                products[index].update(update_data)

        # Update context with modified product data
        context.update({"produtos": products})
        logger.info("Test completed: test_if_product_can_be_updated")

    def test_if_product_can_be_deleted(
        self,
        login_user,
        random_admin_token,
        create_product,
        context,
    ):
        """Ensure product deletion responds with success message."""
        logger.info("Starting test: test_if_product_can_be_deleted")
        token = random_admin_token
        product_ids = context.get("produto_ids")

        if not product_ids:
            logger.error("No product IDs found in context")
            raise ValueError("No product IDs found in context")

        logger.info(f"Deleting {len(product_ids)} product(s)")
        with soft_assertions():
            for idx, product_id in enumerate(product_ids):
                _id = product_id
                logger.info(f"Deleting product {idx + 1} with ID: {_id}")

                # Delete product using admin token
                response = self.client.delete_product(_id, token)

                # Verify successful deletion
                assert_that(response.status_code).is_equal_to(200)
                logger.debug(f"Product {idx + 1} - Status code: {response.status_code}")
                assert_that(response.as_dict).is_not_empty()
                assert_that(response.as_dict["message"]).contains("Registro excluído com sucesso")
                logger.info(f"Product {idx + 1} deleted successfully")

        logger.info("Test completed: test_if_product_can_be_deleted")

"""Tests for ServeRest users endpoints."""

import logging

from assertpy import assert_that, soft_assertions

from services.serverest_api.api.users import Users

logger = logging.getLogger(__name__)


class TestUsers:
    """Exercises primary CRUD flows for users."""

    client = Users()

    def test_if_user_can_be_created(self, create_user, context):
        """Ensure user creation works and returns ids."""
        logger.info("Starting test: test_if_user_can_be_created")
        responses = create_user
        logger.info(f"Created {len(responses)} user(s)")

        with soft_assertions():
            for idx, response in enumerate(responses):
                logger.info(f"Verifying user {idx + 1} creation response")
                # Verify successful creation status code
                assert_that(response.status_code).is_equal_to(201)
                logger.debug(f"User {idx + 1} - Status code: {response.status_code}")

                # Verify response contains data
                assert_that(response.as_dict).is_not_empty()
                logger.debug(f"User {idx + 1} - Response data: {response.as_dict}")

                # Verify success message
                assert_that(response.as_dict["message"]).contains("Cadastro realizado com sucesso")
                logger.debug(f"User {idx + 1} - Success message verified")

                # Verify user ID is present and not null
                assert_that(response.as_dict).contains("_id")
                assert_that(response.as_dict["_id"]).is_not_none()
                logger.info(f"User {idx + 1} created successfully with ID: {response.as_dict['_id']}")

        logger.info("Test completed: test_if_user_can_be_created")

    def test_if_user_can_be_fetched(self, create_user, context):
        """Confirm filtered user queries match context data."""
        logger.info("Starting test: test_if_user_can_be_fetched")
        users = context.get("usuarios")

        if not users:
            logger.error("No users found in context")
            raise ValueError("No users found in context")

        logger.info(f"Fetching {len(users)} user(s) with filters")
        with soft_assertions():
            for idx, user_data in enumerate(users):
                # Extract user data for filtering
                _id = user_data["_id"]
                name = user_data["nome"]
                email = user_data["email"]
                is_admin = user_data["administrador"]
                logger.info(f"Fetching user {idx + 1} - ID: {_id}, Name: {name}, Email: {email}")

                # Retrieve user with filter parameters
                response = self.client.get_user(
                    _id=_id,
                    nome=name,
                    email=email,
                    administrador=is_admin,
                )

                # Verify successful retrieval
                assert_that(response.status_code).is_equal_to(200)
                logger.debug(f"User {idx + 1} - Status code: {response.status_code}")
                assert_that(response.as_dict).is_not_empty()

                # Verify returned user data matches created data
                assert_that(response.as_dict).contains("usuarios")
                for user in response.as_dict.get("usuarios", []):
                    assert_that(user["_id"]).is_equal_to(_id)
                    assert_that(user["nome"]).is_equal_to(name)
                    assert_that(user["email"]).is_equal_to(email)
                    assert_that(user["administrador"]).is_equal_to(is_admin)
                logger.info(f"User {idx + 1} fetched and verified successfully")

        logger.info("Test completed: test_if_user_can_be_fetched")

    def test_if_user_can_be_fetched_by_id(self, create_user, context):
        """Check detail endpoint returns stored values."""
        logger.info("Starting test: test_if_user_can_be_fetched_by_id")
        users = context.get("usuarios")

        if not users:
            logger.error("No users found in context")
            raise ValueError("No users found in context")

        logger.info(f"Fetching {len(users)} user(s) by ID")
        with soft_assertions():
            for idx, user_data in enumerate(users):
                # Extract user data for verification
                _id = user_data["_id"]
                name = user_data["nome"]
                email = user_data["email"]
                is_admin = user_data["administrador"]
                logger.info(f"Fetching user {idx + 1} by ID: {_id}")

                # Retrieve user by ID
                response = self.client.get_user_by_id(_id)

                # Verify successful retrieval
                assert_that(response.status_code).is_equal_to(200)
                logger.debug(f"User {idx + 1} - Status code: {response.status_code}")
                assert_that(response.as_dict).is_not_empty()

                # Verify returned user data matches created data
                assert_that(response.as_dict["_id"]).is_equal_to(_id)
                assert_that(response.as_dict["nome"]).is_equal_to(name)
                assert_that(response.as_dict["email"]).is_equal_to(email)
                assert_that(response.as_dict["administrador"]).is_equal_to(is_admin)
                logger.info(f"User {idx + 1} fetched by ID and verified successfully")

        logger.info("Test completed: test_if_user_can_be_fetched_by_id")

    def test_if_user_can_be_updated(self, create_user, context, user_data_for_update):
        """Ensure update calls succeed with replacement payloads."""
        logger.info("Starting test: test_if_user_can_be_updated")
        users = context.get("usuarios")

        if not users:
            logger.error("No users found in context")
            raise ValueError("No users found in context")

        logger.info(f"Updating {len(users)} user(s)")
        with soft_assertions():
            for index, user_data in enumerate(users):
                _id = user_data["_id"]
                logger.info(f"Updating user {index + 1} with ID: {_id}")

                # Validate update data availability
                if not user_data_for_update or "usuarios" not in user_data_for_update:
                    logger.error("User data for update not found")
                    raise ValueError("User data for update not found")
                if index >= len(user_data_for_update["usuarios"]):
                    logger.error(f"Update data not available for user index {index}")
                    raise ValueError(f"Update data not available for user index {index}")

                update_data = user_data_for_update["usuarios"][index]
                logger.debug(f"User {index + 1} - Update data: {update_data}")

                # Update user with new data
                response = self.client.update_user(_id, update_data)

                # Verify successful update
                assert_that(response.status_code).is_equal_to(200)
                logger.debug(f"User {index + 1} - Status code: {response.status_code}")
                assert_that(response.as_dict).is_not_empty()
                assert_that(response.as_dict["message"]).contains("Registro alterado com sucesso")
                logger.info(f"User {index + 1} updated successfully")

                # Update local user data for consistency
                users[index].update(update_data)

        # Update context with modified user data
        context.update({"usuarios": users})
        logger.info("Test completed: test_if_user_can_be_updated")

    def test_if_user_can_be_deleted(self, create_user, context):
        """Ensure deletion reports success for each user."""
        logger.info("Starting test: test_if_user_can_be_deleted")
        users = context.get("usuarios")

        if not users:
            logger.warning("No users found in context for deletion")
        else:
            logger.info(f"Deleting {len(users)} user(s)")

        with soft_assertions():
            for idx, user_data in enumerate(users):
                _id = user_data["_id"]
                logger.info(f"Deleting user {idx + 1} with ID: {_id}")

                # Delete user
                response = self.client.delete_user(_id)

                # Verify successful deletion
                assert_that(response.status_code).is_equal_to(200)
                logger.debug(f"User {idx + 1} - Status code: {response.status_code}")
                assert_that(response.as_dict).is_not_empty()
                assert_that(response.as_dict["message"]).contains("Registro excluído com sucesso")
                logger.info(f"User {idx + 1} deleted successfully")

        logger.info("Test completed: test_if_user_can_be_deleted")

"""Tests for ServeRest login endpoint."""

import logging

from assertpy import assert_that, soft_assertions

from services.serverest_api.api.login import Login

logger = logging.getLogger(__name__)


class TestLogin:
    """Covers basic authentication happy paths."""

    client = Login()

    def test_if_user_can_be_login(self, login_user, context):
        """Ensure a login attempt returns tokens for each user."""
        logger.info("Starting test: test_if_user_can_be_login")
        responses = login_user
        logger.info(f"Logged in {len(responses)} user(s)")

        with soft_assertions():
            for idx, response in enumerate(responses):
                logger.info(f"Verifying user {idx + 1} login response")
                # Verify successful login status code
                assert_that(response.status_code).is_equal_to(200)
                logger.debug(f"User {idx + 1} - Status code: {response.status_code}")

                # Verify response contains data
                assert_that(response.as_dict).is_not_empty()
                logger.debug(f"User {idx + 1} - Response data: {response.as_dict}")

                # Verify success message
                assert_that(response.as_dict["message"]).contains("Login realizado com sucesso")
                logger.debug(f"User {idx + 1} - Success message verified")

                # Verify authorization token is present and not null
                assert_that(response.as_dict).contains("authorization")
                assert_that(response.as_dict["authorization"]).is_not_none()
                logger.info(f"User {idx + 1} logged in successfully with authorization token")

        logger.info("Test completed: test_if_user_can_be_login")

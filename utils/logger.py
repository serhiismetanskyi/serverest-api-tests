import datetime
import logging
import os
import pathlib
from pathlib import Path

from requests import Response

logger = logging.getLogger(__name__)


class Logger:
    """Persist HTTP requests and responses for debugging."""

    dir_path = pathlib.Path(__file__).parent.parent
    file_name = f"log_{str(datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))}.log"
    logs_dir = Path(dir_path, "./logs")
    file_path = Path(logs_dir, file_name)

    @classmethod
    def _ensure_logs_dir(cls):
        """Create logs directory if it doesn't exist."""
        cls.logs_dir.mkdir(parents=True, exist_ok=True)

    @classmethod
    def write_log_to_file(cls, data: str):
        """Append the given string to the log file."""
        cls._ensure_logs_dir()
        with open(cls.file_path, "a", encoding="utf-8") as logger_file:
            logger_file.write(data)

    @classmethod
    def add_request(cls, url: str, method: str, body: str = None, headers: dict = None):
        """Record outgoing request metadata."""
        test_name = os.environ.get("PYTEST_CURRENT_TEST")

        data_to_add = "\n-----\n"
        data_to_add += f"Test: {test_name}\n"
        data_to_add += f"Time: {str(datetime.datetime.now())}\n"
        data_to_add += f"Request method: {method}\n"
        data_to_add += f"Request URL: {url}\n"

        if headers:
            data_to_add += f"Request headers: {headers}\n"

        if body:
            data_to_add += f"Request body: {body}\n"

        data_to_add += "\n"

        cls.write_log_to_file(data_to_add)

        # Also log to standard logger for HTML report
        logger.info(f"HTTP {method} Request: {url}")
        if body:
            logger.debug(f"Request body: {body[:200]}..." if len(body) > 200 else f"Request body: {body}")

    @classmethod
    def add_response(cls, result: Response):
        """Record response metadata and body."""
        cookies_as_dict = dict(result.cookies)
        headers_as_dict = dict(result.headers)

        data_to_add = f"Response code: {result.status_code}\n"
        data_to_add += f"Response text: {result.text}\n"
        data_to_add += f"Response headers: {headers_as_dict}\n"
        data_to_add += f"Response cookies: {cookies_as_dict}\n"
        data_to_add += "\n-----\n"

        cls.write_log_to_file(data_to_add)

        # Also log to standard logger for HTML report
        logger.info(f"HTTP Response: {result.status_code} - {result.url}")
        logger.debug(
            f"Response body: {result.text[:200]}..." if len(result.text) > 200 else f"Response body: {result.text}"
        )

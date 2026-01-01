import json
from pathlib import Path

BASE_PATH = Path.cwd() / "tests" / "data"


class FileManager:
    """Utility helpers for reading and writing JSON fixtures."""

    @staticmethod
    def read_file(file_name: str) -> dict:
        """Return JSON content for the requested file."""
        file_path = FileManager.get_file_with_json_ext(file_name)
        try:
            with open(file_path, encoding="utf-8") as file:
                return json.load(file)
        except FileNotFoundError as exc:
            raise FileNotFoundError(
                f"File {file_name} not found at {file_path}. Ensure the file is created first."
            ) from exc

    @staticmethod
    def update_file(file_name, data):
        """Merge the given payload into the target JSON file."""
        file_path = FileManager.get_file_with_json_ext(file_name)
        try:
            with open(file_path, encoding="utf-8") as file:
                json_data = json.load(file)
        except FileNotFoundError:
            # Create file with empty dict if it doesn't exist
            json_data = {}

        json_data.update(data)
        with open(file_path, mode="w", encoding="utf-8") as file:
            json.dump(json_data, file, indent=4)

    @staticmethod
    def clear_file(file_name):
        """Overwrite the target JSON file with an empty object."""
        file_path = FileManager.get_file_with_json_ext(file_name)
        json_data = {}
        with open(file_path, mode="w", encoding="utf-8") as file:
            json.dump(json_data, file, indent=4)

    @staticmethod
    def get_file_with_json_ext(file_name: str) -> Path:
        """Return the canonical path under tests/data for the given name."""
        if not file_name.endswith(".json"):
            file_name += ".json"
        return BASE_PATH / file_name

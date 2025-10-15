import pytest
import requests
import yaml
import os
import pathlib
from typing import Dict, Any


def load_config():
    """Load configuration from a YAML file and replace environment variables."""
    config_path = pathlib.Path(__file__).parent / "config.yml"
    with open(config_path, "r") as file:
        config = yaml.safe_load(file)

    def replace_env_vars(value):
        if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
            env_var = value[2:-1]
            return os.getenv(env_var, value)  # Default to the string if environment variable is not found
        return value

    def recursive_replace(obj):
        if isinstance(obj, dict):
            return {k: recursive_replace(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [recursive_replace(item) for item in obj]
        else:
            return replace_env_vars(obj)

    return recursive_replace(config)


@pytest.fixture(scope="session")
def config():
    """Fixture to provide the loaded configuration."""
    return load_config()


class APIHelper:
    """Helper class for making HTTP requests."""

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    def make_request(self, endpoint: str, params=None, headers=None, method="GET"):
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        response = requests.request(method, url, params=params, headers=headers)
        return response


@pytest.fixture(scope="session")
def api_helper(config):
    """Fixture to provide the API helper class."""
    base_url = config["api"]["host"]
    return APIHelper(base_url)


class APIClient:
    """Simple API client for GET requests."""

    def __init__(self, api_helper: APIHelper):
        self.api_helper = api_helper

    def get(self, endpoint: str, headers=None, params=None):
        return self.api_helper.make_request(endpoint, params=params, headers=headers, method="GET")


@pytest.fixture(scope="session")
def api_client(api_helper):
    """Fixture to provide the API client."""
    return APIClient(api_helper)


@pytest.fixture(scope="session")
def valid_api_key(config):
    """Fixture to provide a valid API key."""
    return config["authentication"]["api_key"]


@pytest.fixture(scope="session")
def invalid_api_key():
    """Fixture to provide an invalid API key."""
    return "INVALID_API_KEY"


@pytest.fixture(scope="session")
def valid_location():
    """Fixture to provide a valid location parameter."""
    return "New York"  # Example location


@pytest.fixture(scope="session")
def oauth2_token(config):
    """Fixture to provide the OAuth2 token."""
    return config["authentication"]["petstore_auth"]


class SchemaValidator:
    """Class for schema validation."""

    def validate_order_schema(self, order_data: Dict[str, Any]) -> bool:
        """Validate Order object schema."""
        required_fields = ["id", "petId", "quantity", "shipDate", "status", "complete"]
        return all(field in order_data for field in required_fields)

    def validate_category_schema(self, category_data: Dict[str, Any]) -> bool:
        """Validate Category object schema."""
        required_fields = ["id", "name"]
        return all(field in category_data for field in required_fields)

    def validate_user_schema(self, user_data: Dict[str, Any]) -> bool:
        """Validate User object schema."""
        required_fields = [
            "id", "username", "firstName", "lastName", "email", "password", "phone", "userStatus"
        ]
        return all(field in user_data for field in required_fields)

    def validate_tag_schema(self, tag_data: Dict[str, Any]) -> bool:
        """Validate Tag object schema."""
        required_fields = ["id", "name"]
        return all(field in tag_data for field in required_fields)

    def validate_pet_schema(self, pet_data: Dict[str, Any]) -> bool:
        """Validate Pet object schema."""
        required_fields = ["name", "photoUrls"]
        if not all(field in pet_data for field in required_fields):
            return False

        # Validate nested fields if present
        category_validator = self.validate_category_schema
        tags_validator = self.validate_tag_schema

        if "category" in pet_data and isinstance(pet_data["category"], dict):
            if not category_validator(pet_data["category"]):
                return False

        if "tags" in pet_data and isinstance(pet_data["tags"], list):
            for tag in pet_data["tags"]:
                if not tags_validator(tag):
                    return False

        return True

    def validate_api_response_schema(self, api_response_data: Dict[str, Any]) -> bool:
        """Validate ApiResponse object schema."""
        required_fields = ["code", "type", "message"]
        return all(field in api_response_data for field in required_fields)


@pytest.fixture(scope="session")
def schema_validator():
    """Fixture to provide the SchemaValidator class."""
    return SchemaValidator()

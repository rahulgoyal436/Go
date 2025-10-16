import os
import pytest
import requests
import yaml
from pathlib import Path
from typing import Dict, Any


@pytest.fixture(scope="session")
def config():
    """Load configuration from config.yml and replace env variables."""
    config_path = Path(__file__).parent / "config.yml"
    with config_path.open("r") as file:
        raw_config = yaml.safe_load(file)

    def resolve_env_vars(value):
        """Replace ${var} with environment variable values."""
        if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
            env_var = value[2:-1]
            return os.getenv(env_var, None)
        return value

    def recursively_resolve(item):
        if isinstance(item, dict):
            return {k: recursively_resolve(v) for k, v in item.items()}
        elif isinstance(item, list):
            return [recursively_resolve(i) for i in item]
        else:
            return resolve_env_vars(item)

    return recursively_resolve(raw_config)


@pytest.fixture(scope="session")
def api_helper(config):
    """Helper class for making HTTP requests."""
    class APIHelper:
        def __init__(self, base_url):
            self.base_url = base_url.rstrip("/")

        def make_request(self, endpoint, params=None, headers=None, method="GET", data=None, json=None):
            url = f"{self.base_url}/{endpoint.lstrip('/')}"
            response = requests.request(
                method,
                url,
                params=params,
                headers=headers,
                data=data,
                json=json
            )
            return response

    base_url = config["api"]["host"].strip()
    return APIHelper(base_url)


@pytest.fixture(scope="session")
def api_client(api_helper):
    """Simple API client with commonly used request methods."""
    class APIClient:
        def get(self, endpoint, headers=None, params=None):
            return api_helper.make_request(endpoint, headers=headers, params=params, method="GET")

        def post(self, endpoint, headers=None, data=None, json=None):
            return api_helper.make_request(endpoint, headers=headers, data=data, json=json, method="POST")

        def put(self, endpoint, headers=None, data=None, json=None):
            return api_helper.make_request(endpoint, headers=headers, data=data, json=json, method="PUT")

        def delete(self, endpoint, headers=None, params=None):
            return api_helper.make_request(endpoint, headers=headers, params=params, method="DELETE")

    return APIClient()


@pytest.fixture(scope="session")
def valid_api_key(config):
    """Extract a valid API key from the config."""
    return config["authentication"]["api_key"]


@pytest.fixture(scope="session")
def invalid_api_key():
    """Provide a dummy invalid API key."""
    return "INVALID_API_KEY"


@pytest.fixture(scope="session")
def valid_location():
    """Provide a valid location parameter."""
    return "default_location"


@pytest.fixture(scope="session")
def oauth2_token(config):
    """Extract OAuth2 token from the config."""
    return config["authentication"]["petstore_auth"]


class SchemaValidator:
    """Dynamic schema validation functions based on components schema."""

    def validate_order_schema(self, order_data: Dict[str, Any]) -> bool:
        """Validate Order object schema."""
        required_fields = ['id', 'petId', 'quantity', 'shipDate', 'status', 'complete']
        return all(field in order_data for field in required_fields)

    def validate_category_schema(self, category_data: Dict[str, Any]) -> bool:
        """Validate Category object schema."""
        required_fields = []
        return all(field in category_data for field in required_fields)

    def validate_user_schema(self, user_data: Dict[str, Any]) -> bool:
        """Validate User object schema."""
        required_fields = ['id', 'username', 'firstName', 'lastName', 'email', 'password', 'phone', 'userStatus']
        return all(field in user_data for field in required_fields)

    def validate_tag_schema(self, tag_data: Dict[str, Any]) -> bool:
        """Validate Tag object schema."""
        required_fields = []
        return all(field in tag_data for field in required_fields)

    def validate_pet_schema(self, pet_data: Dict[str, Any]) -> bool:
        """Validate Pet object schema."""
        required_fields = ['name', 'photoUrls']
        if not all(field in pet_data for field in required_fields):
            return False
        if "category" in pet_data:
            if not self.validate_category_schema(pet_data["category"]):
                return False
        if "tags" in pet_data:
            if not all(self.validate_tag_schema(tag) for tag in pet_data["tags"]):
                return False
        return True

    def validate_api_response_schema(self, api_response_data: Dict[str, Any]) -> bool:
        """Validate ApiResponse object schema."""
        required_fields = []
        return all(field in api_response_data for field in required_fields)


@pytest.fixture(scope="session")
def schema_validator():
    """Provide an instance of SchemaValidator for schema validations."""
    return SchemaValidator()

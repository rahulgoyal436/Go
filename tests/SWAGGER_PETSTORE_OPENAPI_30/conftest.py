import pytest
import requests
import yaml
import os
from pathlib import Path
from typing import Dict, Any


@pytest.fixture(scope="session")
def config():
    """Load and provide the configuration from a YAML file."""
    config_path = Path(__file__).parent / "config.yml"
    try:
        with open(config_path, "r") as f:
            config_data = yaml.safe_load(f)

        # Replace environment variables in config
        def replace_env_var(value):
            if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
                env_var = value[2:-1]
                return os.getenv(env_var, "")
            return value

        def parse_config(data):
            if isinstance(data, dict):
                return {k: parse_config(v) for k, v in data.items()}
            elif isinstance(data, list):
                return [parse_config(v) for v in data]
            else:
                return replace_env_var(data)

        return parse_config(config_data)
    except FileNotFoundError:
        raise FileNotFoundError("Configuration file 'config.yml' not found.")
    except yaml.YAMLError:
        raise ValueError("Error while parsing the configuration file.")


class APIHelper:
    """Helper class to make HTTP requests."""

    def __init__(self, base_url: str):
        self.base_url = base_url.strip()

    def make_request(self, endpoint: str, params=None, headers=None, method="GET") -> requests.Response:
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        try:
            response = requests.request(method, url, params=params, headers=headers)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            pytest.fail(f"API request failed: {e}")


@pytest.fixture(scope="session")
def api_helper(config):
    """Provide an APIHelper instance."""
    base_url = config["api"]["host"]
    return APIHelper(base_url)


class APIClient:
    """Simple API client for GET and other HTTP operations."""

    def __init__(self, api_helper: APIHelper):
        self.api_helper = api_helper

    def get(self, endpoint: str, headers=None, params=None) -> Dict[str, Any]:
        response = self.api_helper.make_request(endpoint, params=params, headers=headers, method="GET")
        return response.json()


@pytest.fixture(scope="session")
def api_client(api_helper):
    """Provide an APIClient instance."""
    return APIClient(api_helper)


@pytest.fixture(scope="session")
def valid_api_key(config):
    """Extract a valid API key from the configuration."""
    return config["authentication"]["api_key"]


@pytest.fixture(scope="session")
def invalid_api_key():
    """Provide an invalid API key for testing."""
    return "INVALID_API_KEY_123"


@pytest.fixture(scope="session")
def valid_location():
    """Provide a valid test location for API queries."""
    return {"country": "US"}


@pytest.fixture(scope="session")
def oauth2_token(config):
    """Extract OAuth2 token from config."""
    return config["authentication"]["petstore_auth"]


class SchemaValidator:
    """Class for schema validation."""

    @staticmethod
    def validate_schema_order(order_data: Dict[str, Any]) -> bool:
        """Validate Order object schema."""
        required_fields = ['id', 'petId', 'quantity', 'shipDate', 'status', 'complete']
        return all(field in order_data for field in required_fields)

    @staticmethod
    def validate_schema_category(category_data: Dict[str, Any]) -> bool:
        """Validate Category object schema."""
        required_fields = ['id', 'name']
        return all(field in category_data for field in required_fields)

    @staticmethod
    def validate_schema_user(user_data: Dict[str, Any]) -> bool:
        """Validate User object schema."""
        required_fields = ['id', 'username', 'firstName', 'lastName', 'email', 'password', 'phone', 'userStatus']
        return all(field in user_data for field in required_fields)

    @staticmethod
    def validate_schema_tag(tag_data: Dict[str, Any]) -> bool:
        """Validate Tag object schema."""
        required_fields = ['id', 'name']
        return all(field in tag_data for field in required_fields)

    @staticmethod
    def validate_schema_pet(pet_data: Dict[str, Any]) -> bool:
        """Validate Pet object schema."""
        required_fields = ['name', 'photoUrls']
        if not all(field in pet_data for field in required_fields):
            return False
        # Validate nested fields, if applicable
        if 'category' in pet_data and not SchemaValidator.validate_schema_category(pet_data['category']):
            return False
        if 'tags' in pet_data:
            for tag in pet_data['tags']:
                if not SchemaValidator.validate_schema_tag(tag):
                    return False
        return True

    @staticmethod
    def validate_schema_api_response(api_response: Dict[str, Any]) -> bool:
        """Validate ApiResponse object schema."""
        required_fields = ['code', 'type', 'message']
        return all(field in api_response for field in required_fields)


@pytest.fixture(scope="session")
def schema_validator():
    """Provide a SchemaValidator instance."""
    return SchemaValidator()

import pytest
import os
import yaml
from pathlib import Path
import requests
from typing import Any, Dict


class APIHelper:
    """Helper class for making HTTP requests."""
    def __init__(self, base_url: str):
        self.base_url = base_url

    def make_request(self, endpoint: str, params=None, headers=None, method='GET'):
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        if method.upper() == 'GET':
            response = requests.get(url, params=params, headers=headers)
        elif method.upper() == 'POST':
            response = requests.post(url, json=params, headers=headers)
        elif method.upper() == 'PUT':
            response = requests.put(url, json=params, headers=headers)
        elif method.upper() == 'DELETE':
            response = requests.delete(url, params=params, headers=headers)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
        response.raise_for_status()
        return response.json()


class SchemaValidator:
    """Schema Validator class with methods for validation."""

    def validate_order_schema(self, order_data: Dict[str, Any]) -> bool:
        """Validate Order object schema."""
        required_fields = ['id', 'petId', 'quantity', 'shipDate', 'status', 'complete']
        return all(field in order_data for field in required_fields)

    def validate_category_schema(self, category_data: Dict[str, Any]) -> bool:
        """Validate Category object schema."""
        required_fields = ['id', 'name']
        return all(field in category_data for field in required_fields)

    def validate_user_schema(self, user_data: Dict[str, Any]) -> bool:
        """Validate User object schema."""
        required_fields = ['id', 'username', 'firstName', 'lastName', 'email', 'password', 'phone', 'userStatus']
        return all(field in user_data for field in required_fields)

    def validate_tag_schema(self, tag_data: Dict[str, Any]) -> bool:
        """Validate Tag object schema."""
        required_fields = ['id', 'name']
        return all(field in tag_data for field in required_fields)

    def validate_pet_schema(self, pet_data: Dict[str, Any]) -> bool:
        """Validate Pet object schema."""
        required_fields = ['name', 'photoUrls']
        if not all(field in pet_data for field in required_fields):
            return False

        # Validate nested category schema
        if 'category' in pet_data:
            category_fields = ['id', 'name']
            if not all(field in pet_data['category'] for field in category_fields):
                return False

        # Validate nested tags schema
        if 'tags' in pet_data:
            for tag in pet_data['tags']:
                tag_fields = ['id', 'name']
                if not all(field in tag for field in tag_fields):
                    return False

        return True

    def validate_api_response_schema(self, response_data: Dict[str, Any]) -> bool:
        """Validate ApiResponse object schema."""
        required_fields = ['code', 'type', 'message']
        return all(field in response_data for field in required_fields)


@pytest.fixture(scope="session")
def config():
    """Load configuration from a YAML file."""
    config_path = Path(__file__).parent / "config.yml"
    try:
        with open(config_path, 'r') as file:
            raw_config = yaml.safe_load(file)

        def replace_env_var(value):
            if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
                env_var = value[2:-1]
                return os.getenv(env_var, value)
            return value

        parsed_config = {}
        for key, val in raw_config.items():
            if isinstance(val, dict):
                parsed_config[key] = {k: replace_env_var(v) for k, v in val.items()}
            else:
                parsed_config[key] = replace_env_var(val)
        return parsed_config
    except FileNotFoundError:
        pytest.fail("Configuration file not found.")
    except yaml.YAMLError as e:
        pytest.fail(f"Error parsing YAML configuration file: {e}")


@pytest.fixture(scope="session")
def api_helper(config):
    """Provide an API helper instance."""
    base_url = config["api"]["host"].strip()
    return APIHelper(base_url)


@pytest.fixture(scope="session")
def api_client(api_helper):
    """Provide a simplified API client."""
    class APIClient:
        def __init__(self, helper):
            self.helper = helper

        def get(self, endpoint, headers=None, params=None):
            return self.helper.make_request(endpoint, params=params, headers=headers, method="GET")

    return APIClient(api_helper)


@pytest.fixture()
def valid_api_key(config):
    """Provide a valid API key."""
    return config["authentication"]["api_key"]


@pytest.fixture()
def invalid_api_key():
    """Provide an invalid API key."""
    return "INVALID_API_KEY"


@pytest.fixture()
def valid_location():
    """Provide a valid location parameter."""
    return {"latitude": 40.7128, "longitude": -74.0060}


@pytest.fixture()
def oauth2_token(config):
    """Provide an OAuth2 token."""
    return config["authentication"]["petstore_auth"]


@pytest.fixture(scope="session")
def schema_validator():
    """Provide an instance of the SchemaValidator class."""
    return SchemaValidator()

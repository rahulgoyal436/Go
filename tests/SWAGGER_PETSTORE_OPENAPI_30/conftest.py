import os
import pytest
import requests
import yaml
from pathlib import Path
from typing import Any, Dict


class APIHelper:
    """Helper class for making HTTP API requests."""

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')

    def make_request(self, endpoint: str, params=None, headers=None, method='GET'):
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        response = requests.request(method, url, headers=headers, params=params)
        return response


class SchemaValidator:
    """Dynamic schema validation class."""

    def validate_schema_order(self, order_data: Dict[str, Any]) -> bool:
        """Validate Order object schema."""
        required_fields = ['id', 'petId', 'quantity', 'shipDate', 'status', 'complete']
        return all(field in order_data for field in required_fields)

    def validate_schema_category(self, category_data: Dict[str, Any]) -> bool:
        """Validate Category object schema."""
        required_fields = ['id', 'name']
        return all(field in category_data for field in required_fields)

    def validate_schema_user(self, user_data: Dict[str, Any]) -> bool:
        """Validate User object schema."""
        required_fields = ['id', 'username', 'firstName', 'lastName', 'email', 'password', 'phone', 'userStatus']
        return all(field in user_data for field in required_fields)

    def validate_schema_tag(self, tag_data: Dict[str, Any]) -> bool:
        """Validate Tag object schema."""
        required_fields = ['id', 'name']
        return all(field in tag_data for field in required_fields)

    def validate_schema_pet(self, pet_data: Dict[str, Any]) -> bool:
        """Validate Pet object schema."""
        required_fields = ['name', 'photoUrls']
        top_level_valid = all(field in pet_data for field in required_fields)
        if 'category' in pet_data and isinstance(pet_data['category'], dict):
            category_fields = ['id', 'name']
            category_valid = all(field in pet_data['category'] for field in category_fields)
        else:
            category_valid = True
        return top_level_valid and category_valid

    def validate_schema_api_response(self, api_response_data: Dict[str, Any]) -> bool:
        """Validate ApiResponse object schema."""
        required_fields = ['code', 'type', 'message']
        return all(field in api_response_data for field in required_fields)


@pytest.fixture(scope="session")
def config():
    """Load configuration from YAML file."""
    config_file = Path(__file__).parent / 'config.yml'
    try:
        with open(config_file, 'r', encoding='utf-8') as file:
            raw_config = yaml.safe_load(file)

        # Resolve environment variables in config
        def resolve_env(value):
            return os.getenv(value[2:-1], value) if value.startswith('${') and value.endswith('}') else value

        def resolve_nested(item):
            if isinstance(item, dict):
                return {k: resolve_nested(v) for k, v in item.items()}
            elif isinstance(item, list):
                return [resolve_nested(i) for i in item]
            elif isinstance(item, str):
                return resolve_env(item)
            else:
                return item

        resolved_config = resolve_nested(raw_config)
        return resolved_config
    except Exception as e:
        raise RuntimeError(f"Failed to load configuration: {e}")


@pytest.fixture(scope="session")
def api_helper(config):
    """Fixture to provide APIHelper."""
    base_url = config['api']['host']
    return APIHelper(base_url)


@pytest.fixture(scope="session")
def api_client(api_helper):
    """Fixture to provide a simple API client."""
    class APIClient:
        def get(self, endpoint, headers=None, params=None):
            return api_helper.make_request(endpoint, params=params, headers=headers, method='GET')

    return APIClient()


@pytest.fixture(scope="session")
def valid_api_key(config):
    """Extract valid API key from configuration."""
    return config['authentication']['api_key']


@pytest.fixture(scope="session")
def invalid_api_key():
    """Provides an invalid API key for testing."""
    return "INVALID_API_KEY"


@pytest.fixture(scope="session")
def valid_location():
    """Provide a valid test location parameter."""
    return {"country": "USA", "city": "New York"}


@pytest.fixture(scope="session")
def oauth2_token(config):
    """Extract OAuth2 token from configuration."""
    return config['authentication']['petstore_auth']


@pytest.fixture(scope="session")
def schema_validator():
    """Provide schema validator instance."""
    return SchemaValidator()

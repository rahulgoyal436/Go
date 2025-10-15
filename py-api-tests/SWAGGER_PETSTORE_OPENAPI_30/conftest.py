import os
import pytest
import requests
import yaml
from pathlib import Path


@pytest.fixture(scope='session')
def config():
    """Load configuration from config.yml file."""
    config_path = Path(__file__).parent / 'config.yml'
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found at {config_path}")
    
    with open(config_path, 'r') as file:
        config_data = yaml.safe_load(file)
    
    def resolve_env_vars(value):
        """Replace ${var} with environment variable value."""
        if isinstance(value, str) and value.startswith('${') and value.endswith('}'):
            env_var = value[2:-1]
            return os.environ.get(env_var, '')
        return value
    
    def resolve_recursively(data):
        """Recursively replace environment variables in dictionary."""
        if isinstance(data, dict):
            return {key: resolve_recursively(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [resolve_recursively(item) for item in data]
        else:
            return resolve_env_vars(data)
    
    return resolve_recursively(config_data)


class APIHelper:
    """Helper class for making HTTP requests."""
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
    
    def make_request(self, endpoint, params=None, headers=None, method='GET'):
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        response = requests.request(method, url, params=params, headers=headers)
        return response


@pytest.fixture(scope='session')
def api_helper(config):
    """Fixture to provide APIHelper instance."""
    base_url = config['api']['host']
    return APIHelper(base_url)


class APIClient:
    """Simple API client for common operations."""
    def __init__(self, helper: APIHelper):
        self.helper = helper
    
    def get(self, endpoint, headers=None, params=None):
        return self.helper.make_request(endpoint, params=params, headers=headers, method='GET')


@pytest.fixture(scope='session')
def api_client(api_helper):
    """Fixture to provide APIClient instance."""
    return APIClient(api_helper)


@pytest.fixture(scope='session')
def valid_api_key(config):
    """Fixture to provide valid API key."""
    return config['authentication']['api_key']


@pytest.fixture(scope='session')
def invalid_api_key():
    """Fixture to provide invalid API key."""
    return "INVALID_API_KEY"


@pytest.fixture(scope='session')
def valid_location():
    """Fixture to provide valid location for testing."""
    return {"latitude": 37.7749, "longitude": -122.4194}


@pytest.fixture(scope='session')
def oauth2_token(config):
    """Fixture to provide OAuth2 token."""
    return config['authentication']['petstore_auth']


# Schema validation utility functions
def validate_order_schema(order_data):
    """Validate Order object schema."""
    required_fields = ['id', 'petId', 'quantity', 'shipDate', 'status', 'complete']
    return all(field in order_data for field in required_fields)


def validate_category_schema(category_data):
    """Validate Category object schema."""
    required_fields = ['id', 'name']
    return all(field in category_data for field in required_fields)


def validate_user_schema(user_data):
    """Validate User object schema."""
    required_fields = ['id', 'username', 'firstName', 'lastName', 'email', 'password', 'phone', 'userStatus']
    return all(field in user_data for field in required_fields)


def validate_tag_schema(tag_data):
    """Validate Tag object schema."""
    required_fields = ['id', 'name']
    return all(field in tag_data for field in required_fields)


def validate_pet_schema(pet_data):
    """Validate Pet object schema."""
    required_fields = ['name', 'photoUrls']
    if not all(field in pet_data for field in required_fields):
        return False
    
    # Validate nested fields
    if 'category' in pet_data:
        category = pet_data['category']
        if not validate_category_schema(category):
            return False
    
    if 'tags' in pet_data:
        tags = pet_data['tags']
        for tag in tags:
            if not validate_tag_schema(tag):
                return False
    
    return True


def validate_api_response_schema(response_data):
    """Validate ApiResponse object schema."""
    required_fields = ['code', 'type', 'message']
    return all(field in response_data for field in required_fields)


@pytest.fixture(scope='session')
def schema_validators():
    """Fixture to provide all schema validation functions."""
    return {
        "Order": validate_order_schema,
        "Category": validate_category_schema,
        "User": validate_user_schema,
        "Tag": validate_tag_schema,
        "Pet": validate_pet_schema,
        "ApiResponse": validate_api_response_schema,
    }

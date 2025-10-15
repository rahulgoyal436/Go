import os
from pathlib import Path
import pytest
import yaml
import requests
from typing import Dict, Any


@pytest.fixture(scope="session")
def config():
    """Load configuration from config.yml file."""
    config_path = Path(__file__).parent / 'config.yml'
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found at {config_path}")

    with open(config_path, 'r') as file:
        config_data = yaml.safe_load(file)

    def replace_variables(value):
        if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
            env_var = value[2:-1]
            return os.getenv(env_var, "")
        return value

    for section, values in config_data.items():
        if isinstance(values, dict):
            config_data[section] = {key: replace_variables(val) for key, val in values.items()}
        else:
            config_data[section] = replace_variables(values)

    return config_data


class APIHelper:
    """Helper class for making HTTP requests."""
    def __init__(self, base_url):
        self.base_url = base_url.strip()

    def make_request(self, endpoint, params=None, headers=None, method='GET'):
        url = f"{self.base_url}{endpoint}"
        response = requests.request(method, url, params=params, headers=headers)
        return response


@pytest.fixture(scope="session")
def api_helper(config):
    """Fixture providing APIHelper instance."""
    base_url = config['api']['host']
    return APIHelper(base_url)


class APIClient:
    """Simple API Client."""
    def __init__(self, api_helper):
        self.api_helper = api_helper

    def get(self, endpoint, headers=None, params=None):
        return self.api_helper.make_request(endpoint, params=params, headers=headers, method='GET')


@pytest.fixture(scope="session")
def api_client(api_helper):
    """Fixture providing APIClient instance."""
    return APIClient(api_helper)


@pytest.fixture(scope="session")
def valid_api_key(config):
    """Fixture providing valid API key."""
    return config['authentication']['api_key']


@pytest.fixture(scope="session")
def invalid_api_key():
    """Fixture providing dummy invalid API key."""
    return "invalid_api_key"


@pytest.fixture(scope="session")
def valid_location():
    """Fixture providing valid test location parameter."""
    return "New York"


@pytest.fixture(scope="session")
def oauth2_token(config):
    """Fixture extracting OAuth2 token from config."""
    return config['authentication']['petstore_auth']


class SchemaValidator:
    """Schema Validator for components."""
    
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
        top_level_validation = all(field in pet_data for field in required_fields)
        if not top_level_validation:
            return False
        if 'category' in pet_data and 'id' in pet_data['category'] and 'name' in pet_data['category']:
            category = pet_data['category']
            category_valid = 'id' in category and 'name' in category
            if not category_valid:
                return False
        if 'tags' in pet_data and isinstance(pet_data['tags'], list):
            for tag in pet_data['tags']:
                tag_valid = 'id' in tag and 'name' in tag
                if not tag_valid:
                    return False
        return True

    def validate_api_response_schema(self, api_response_data: Dict[str, Any]) -> bool:
        """Validate ApiResponse object schema."""
        required_fields = ['code', 'type', 'message']
        return all(field in api_response_data for field in required_fields)


@pytest.fixture(scope="session")
def schema_validator():
    """Fixture providing SchemaValidator instance."""
    return SchemaValidator()

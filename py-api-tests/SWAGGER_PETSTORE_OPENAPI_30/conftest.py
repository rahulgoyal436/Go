import os
import yaml
import pytest
import requests
from typing import Dict, Any
from pathlib import Path


def load_config():
    """Load configuration from YAML file and replace environment variables."""
    config_path = Path(__file__).parent / "config.yml"
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file '{config_path}' not found.")
    
    with config_path.open("r") as config_file:
        config = yaml.safe_load(config_file)
    
    def resolve_env_vars(val):
        if isinstance(val, str) and val.startswith("${") and val.endswith("}"):
            env_var_name = val[2:-1]
            return os.getenv(env_var_name, None)
        return val
    
    def recursive_resolve(d):
        if isinstance(d, dict):
            return {k: recursive_resolve(v) for k, v in d.items()}
        if isinstance(d, (list, tuple)):
            return [recursive_resolve(v) for v in d]
        return resolve_env_vars(d)
    
    return recursive_resolve(config)


@pytest.fixture(scope="session")
def config():
    """Fixture to load configuration."""
    return load_config()


class ApiHelper:
    """Helper class for making API requests."""
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
    
    def make_request(self, endpoint: str, params=None, headers=None, method='GET'):
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        response = requests.request(method, url, params=params, headers=headers)
        return response


@pytest.fixture(scope="session")
def api_helper(config):
    """Fixture for API helper."""
    base_url = config.get('api', {}).get('host', "").strip()
    if not base_url:
        raise ValueError("Base URL for API is not defined in the configuration file.")
    return ApiHelper(base_url)


class ApiClient(ApiHelper):
    """Simple API Client."""
    def get(self, endpoint: str, headers=None, params=None):
        return self.make_request(endpoint, params=params, headers=headers, method='GET')


@pytest.fixture(scope="session")
def api_client(api_helper):
    """Fixture for API Client."""
    return api_helper


@pytest.fixture(scope="session")
def valid_api_key(config):
    """Fixture to get valid API Key from config."""
    api_key = config.get("authentication", {}).get("api_key", "").strip()
    if not api_key:
        raise ValueError("API key is not defined in the configuration file.")
    return api_key


@pytest.fixture(scope="session")
def invalid_api_key():
    """Fixture to provide a dummy invalid API Key."""
    return "INVALID_API_KEY"


@pytest.fixture(scope="session")
def valid_location():
    """Fixture to provide a sample valid location."""
    return "valid_location_sample"


@pytest.fixture(scope="session")
def oauth2_token(config):
    """Fixture to extract OAuth2 token from configuration."""
    token = config.get("authentication", {}).get("petstore_auth", "").strip()
    if not token:
        raise ValueError("OAuth2 token is not defined in the configuration file.")
    return token


class SchemaValidator:
    """Schema Validator class for component schemas."""

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
        if not all(field in pet_data for field in required_fields):
            return False
        
        # Validate nested Category
        if 'category' in pet_data:
            category_validator = SchemaValidator().validate_schema_category
            if not category_validator(pet_data['category']):
                return False

        # Validate nested Tags
        if 'tags' in pet_data and isinstance(pet_data['tags'], list):
            tag_validator = SchemaValidator().validate_schema_tag
            for tag in pet_data['tags']:
                if not tag_validator(tag):
                    return False
        
        return True

    def validate_schema_api_response(self, response_data: Dict[str, Any]) -> bool:
        """Validate ApiResponse object schema."""
        required_fields = ['code', 'type', 'message']
        return all(field in response_data for field in required_fields)


@pytest.fixture(scope="session")
def schema_validator():
    """Fixture for schema validator."""
    return SchemaValidator()

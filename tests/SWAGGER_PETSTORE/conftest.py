import os
import pytest
import requests
import yaml
from pathlib import Path
from typing import Dict, Any


# Load configuration from YAML file
@pytest.fixture(scope="session")
def config():
    config_path = Path(__file__).parent / "config.yml"
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    with open(config_path, 'r') as file:
        config_data = yaml.safe_load(file)
    
    # Replace ${var} with environment variables
    def resolve_env_var(value):
        if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
            env_var = value[2:-1]
            return os.getenv(env_var, None)
        return value

    resolved_config = {key: resolve_env_var(val) for key, val in config_data.items()}
    return resolved_config


# Helper class for handling API requests
class APIHelper:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    def make_request(self, endpoint, params=None, headers=None, method='GET'):
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        response = requests.request(method, url, params=params, headers=headers)
        return response


@pytest.fixture(scope="session")
def api_helper(config):
    base_url = config.get("api", {}).get("host")
    if not base_url:
        raise RuntimeError("Base URL not found in the configuration file.")
    return APIHelper(base_url)


# Simple API client for common methods
class APIClient:
    def __init__(self, helper: APIHelper):
        self.helper = helper

    def get(self, endpoint, headers=None, params=None):
        return self.helper.make_request(endpoint, params=params, headers=headers, method='GET')


@pytest.fixture(scope="session")
def api_client(api_helper):
    return APIClient(api_helper)


# Fixture for valid API key
@pytest.fixture(scope="session")
def valid_api_key(config):
    api_key = config.get("authentication", {}).get("api_key")
    if not api_key:
        raise RuntimeError("API key not found in the configuration file.")
    return api_key


# Fixture for invalid API key (dummy key for negative testing)
@pytest.fixture(scope="session")
def invalid_api_key():
    return "invalid-api-key-123"


# Fixture for valid location parameter
@pytest.fixture(scope="session")
def valid_location():
    return "New York"


# Fixture for OAuth2 token from the configuration
@pytest.fixture(scope="session")
def oauth2_token(config):
    token = config.get("authentication", {}).get("petstore_auth")
    if not token:
        raise RuntimeError("OAuth2 token not found in the configuration file.")
    return token


# SchemaValidator class for dynamic schema validation methods
class SchemaValidator:
    def validate_schema_order(self, order_data: Dict[str, Any]) -> bool:
        """Validate Order object schema"""
        required_fields = ['id', 'petId', 'quantity', 'shipDate', 'status', 'complete']
        return all(field in order_data for field in required_fields)

    def validate_schema_pet(self, pet_data: Dict[str, Any]) -> bool:
        """Validate Pet object schema"""
        required_fields = ['id', 'category', 'name', 'photoUrls', 'tags', 'status']
        return all(field in pet_data for field in required_fields)

    def validate_schema_user(self, user_data: Dict[str, Any]) -> bool:
        """Validate User object schema"""
        required_fields = ['id', 'username', 'firstName', 'lastName', 'email', 'password', 'phone', 'userStatus']
        return all(field in user_data for field in required_fields)


@pytest.fixture(scope="session")
def schema_validator():
    return SchemaValidator()

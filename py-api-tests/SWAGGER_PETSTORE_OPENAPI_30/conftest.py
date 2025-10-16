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
        raise FileNotFoundError(f"{config_path} does not exist.")
    
    with config_path.open("r") as file:
        raw_config = yaml.safe_load(file)
    
    # Replace environment variable placeholders with actual values
    def replace_env_vars(value):
        if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
            env_var = value[2:-1]
            return os.environ.get(env_var, value)
        return value

    def resolve_env_vars(data):
        if isinstance(data, dict):
            return {k: resolve_env_vars(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [resolve_env_vars(v) for v in data]
        return replace_env_vars(data)
    
    config_data = resolve_env_vars(raw_config)
    return config_data

# Helper class for making HTTP requests
class ApiHelper:
    def __init__(self, base_url):
        self.base_url = base_url.rstrip("/")

    def make_request(self, endpoint, params=None, headers=None, method="GET"):
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        response = requests.request(method, url, params=params, headers=headers)
        return response

@pytest.fixture(scope="session")
def api_helper(config):
    base_url = config.get("api", {}).get("host", "").strip()
    if not base_url:
        raise ValueError("API base URL is missing in configuration.")
    return ApiHelper(base_url)

# Simple API Client
class ApiClient:
    def __init__(self, api_helper):
        self.api_helper = api_helper

    def get(self, endpoint, headers=None, params=None):
        return self.api_helper.make_request(endpoint, params=params, headers=headers, method="GET")

@pytest.fixture(scope="session")
def api_client(api_helper):
    return ApiClient(api_helper)

# Fixture to provide a valid API key
@pytest.fixture(scope="session")
def valid_api_key(config):
    api_key = config.get("authentication", {}).get("api_key")
    if not api_key:
        raise ValueError("Valid API key is missing in configuration.")
    return api_key

# Fixture to provide a dummy invalid API key
@pytest.fixture(scope="session")
def invalid_api_key():
    return "INVALID_API_KEY"

# Fixture to provide a test location parameter
@pytest.fixture(scope="session")
def valid_location():
    return "New York"

# Fixture to provide an OAuth2 token
@pytest.fixture(scope="session")
def oauth2_token(config):
    token = config.get("authentication", {}).get("petstore_auth")
    if not token:
        raise ValueError("OAuth2 token is missing in configuration.")
    return token

# Schema Validation class
class SchemaValidator:
    def validate_order_schema(self, order_data: Dict[str, Any]) -> bool:
        """Validate Order schema"""
        required_fields = ['id', 'petId', 'quantity', 'shipDate', 'status', 'complete']
        return all(field in order_data for field in required_fields)

    def validate_category_schema(self, category_data: Dict[str, Any]) -> bool:
        """Validate Category schema"""
        required_fields = ['id', 'name']
        return all(field in category_data for field in required_fields)

    def validate_user_schema(self, user_data: Dict[str, Any]) -> bool:
        """Validate User schema"""
        required_fields = ['id', 'username', 'firstName', 'lastName', 'email', 'password', 'phone', 'userStatus']
        return all(field in user_data for field in required_fields)

    def validate_tag_schema(self, tag_data: Dict[str, Any]) -> bool:
        """Validate Tag schema"""
        required_fields = ['id', 'name']
        return all(field in tag_data for field in required_fields)

    def validate_pet_schema(self, pet_data: Dict[str, Any]) -> bool:
        """Validate Pet schema"""
        required_fields = ['name', 'photoUrls']
        if not all(field in pet_data for field in required_fields):
            return False
        
        if "category" in pet_data:
            required_category_fields = ['id', 'name']
            category_data = pet_data.get("category", {})
            if not all(field in category_data for field in required_category_fields):
                return False
        
        if "tags" in pet_data and isinstance(pet_data["tags"], list):
            for tag in pet_data["tags"]:
                required_tag_fields = ['id', 'name']
                if not all(field in tag for field in required_tag_fields):
                    return False
        
        return True

    def validate_api_response_schema(self, response_data: Dict[str, Any]) -> bool:
        """Validate ApiResponse schema"""
        required_fields = ['code', 'type', 'message']
        return all(field in response_data for field in required_fields)

@pytest.fixture(scope="session")
def schema_validator():
    return SchemaValidator()

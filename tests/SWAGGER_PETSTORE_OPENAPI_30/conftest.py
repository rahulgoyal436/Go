import pytest
import requests
import yaml
import os
from pathlib import Path

# Load Configuration Fixture
@pytest.fixture(scope="session")
def config():
    config_path = Path(__file__).resolve().parent / "config.yml"
    if not config_path.is_file():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    with open(config_path, "r") as file:
        config_data = yaml.safe_load(file)

    def replace_env_vars(value):
        """Replace ${var} with environment variable."""
        if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
            env_var = value[2:-1]
            return os.getenv(env_var, "")
        return value

    # Replace all environment variable references in the config
    def process_dict(data):
        if isinstance(data, dict):
            return {key: process_dict(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [process_dict(item) for item in data]
        else:
            return replace_env_vars(data)

    return process_dict(config_data)

# API Helper Fixture
@pytest.fixture(scope="session")
def api_helper(config):
    class ApiHelper:
        def __init__(self, base_url):
            self.base_url = base_url.strip()

        def make_request(self, endpoint, params=None, headers=None, method="GET"):
            url = f"{self.base_url}/{endpoint}".strip("/")
            response = requests.request(method, url, headers=headers, params=params)
            return response

    base_url = config["api"]["host"]
    return ApiHelper(base_url)

# API Client Fixture
@pytest.fixture(scope="session")
def api_client(api_helper):
    class ApiClient:
        def __init__(self, helper):
            self.helper = helper

        def get(self, endpoint, headers=None, params=None):
            return self.helper.make_request(endpoint, headers=headers, params=params, method="GET")

    return ApiClient(api_helper)

# Valid API Key Fixture
@pytest.fixture(scope="session")
def valid_api_key(config):
    return config["authentication"]["api_key"]

# Invalid API Key Fixture
@pytest.fixture(scope="session")
def invalid_api_key():
    return "invalid_api_key"

# Valid Location Fixture
@pytest.fixture(scope="session")
def valid_location():
    return {"latitude": 37.7749, "longitude": -122.4194}

# OAuth2 Token Fixture
@pytest.fixture(scope="session")
def oauth2_token(config):
    return config["authentication"]["petstore_auth"]

# Schema Validator Class Fixture
@pytest.fixture(scope="session")
def schema_validator():
    class SchemaValidator:
        def validate_schema_order(self, order_data):
            """Validate Order object schema"""
            required_fields = ['id', 'petId', 'quantity', 'shipDate', 'status', 'complete']
            return all(field in order_data for field in required_fields)
        
        def validate_schema_user(self, user_data):
            """Validate User object schema"""
            required_fields = ['id', 'username', 'firstName', 'lastName', 'email', 'password', 'phone', 'userStatus']
            return all(field in user_data for field in required_fields)

        def validate_schema_pet(self, pet_data):
            """Validate Pet object schema"""
            required_fields = ['id', 'category', 'name', 'photoUrls', 'tags', 'status']
            if 'category' in pet_data:
                category_required_fields = ['id', 'name']
                if not all(field in pet_data['category'] for field in category_required_fields):
                    return False
            return all(field in pet_data for field in required_fields)

    return SchemaValidator()

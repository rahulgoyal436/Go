import os
import pytest
import requests
import yaml
import pathlib
from typing import Dict, Any

# Load configuration from YAML
@pytest.fixture(scope="session")
def config():
    config_path = pathlib.Path(__file__).parent / "config.yml"
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found at {config_path}")
    
    with open(config_path, "r") as f:
        raw_config = yaml.safe_load(f)
    
    def resolve_env_variables(config_data):
        if isinstance(config_data, dict):
            return {k: resolve_env_variables(v) for k, v in config_data.items()}
        elif isinstance(config_data, str) and config_data.startswith("${") and config_data.endswith("}"):
            env_var = config_data[2:-1]
            return os.getenv(env_var, "")
        return config_data

    resolved_config = resolve_env_variables(raw_config)
    return resolved_config


# API Helper
class ApiHelper:
    def __init__(self, base_url: str):
        self.base_url = base_url.strip()

    def make_request(self, endpoint: str, params=None, headers=None, method="GET"):
        url = self.base_url + endpoint
        response = requests.request(method, url, params=params, headers=headers)
        response.raise_for_status()
        return response.json()


@pytest.fixture(scope="session")
def api_helper(config):
    base_url = config["api"]["host"]
    return ApiHelper(base_url)


# API Client
class ApiClient:
    def __init__(self, api_helper: ApiHelper):
        self.api_helper = api_helper

    def get(self, endpoint: str, headers=None, params=None):
        return self.api_helper.make_request(endpoint, params=params, headers=headers, method="GET")


@pytest.fixture(scope="session")
def api_client(api_helper):
    return ApiClient(api_helper)


# Valid API Key
@pytest.fixture(scope="session")
def valid_api_key(config):
    if "authentication" in config and "api_key" in config["authentication"]:
        return config["authentication"]["api_key"]
    raise ValueError("Valid API key not found in config")


# Invalid API Key
@pytest.fixture(scope="session")
def invalid_api_key():
    return "INVALID_API_KEY"


# Valid Location
@pytest.fixture(scope="session")
def valid_location():
    return {"lat": 40.7128, "lon": -74.0060}  # Example: New York City


# OAuth2 Token
@pytest.fixture(scope="session")
def oauth2_token(config):
    if "authentication" in config and "oauth2_token" in config["authentication"]:
        return config["authentication"]["oauth2_token"]
    raise ValueError("OAuth2 token not found in config")


# Schema Validator
class SchemaValidator:
    def validate_order_schema(self, order_data: Dict[str, Any]) -> bool:
        """Validate Order object schema"""
        required_fields = ['id', 'petId', 'quantity', 'shipDate', 'status', 'complete']
        return all(field in order_data for field in required_fields)

    def validate_category_schema(self, category_data: Dict[str, Any]) -> bool:
        """Validate Category object schema"""
        required_fields = ['id', 'name']
        return all(field in category_data for field in required_fields)

    def validate_user_schema(self, user_data: Dict[str, Any]) -> bool:
        """Validate User object schema"""
        required_fields = ['id', 'username', 'firstName', 'lastName', 'email', 'password', 'phone', 'userStatus']
        return all(field in user_data for field in required_fields)

    def validate_tag_schema(self, tag_data: Dict[str, Any]) -> bool:
        """Validate Tag object schema"""
        required_fields = ['id', 'name']
        return all(field in tag_data for field in required_fields)

    def validate_pet_schema(self, pet_data: Dict[str, Any]) -> bool:
        """Validate Pet object schema"""
        required_fields = ['name', 'photoUrls']
        if not all(field in pet_data for field in required_fields):
            return False
        
        if "category" in pet_data:
            category_validator = self.validate_category_schema(pet_data["category"])
            if not category_validator:
                return False
        
        if "tags" in pet_data and isinstance(pet_data["tags"], list):
            for tag in pet_data["tags"]:
                tag_validator = self.validate_tag_schema(tag)
                if not tag_validator:
                    return False
        
        return True

    def validate_api_response_schema(self, response_data: Dict[str, Any]) -> bool:
        """Validate ApiResponse object schema"""
        required_fields = ['code', 'type', 'message']
        return all(field in response_data for field in required_fields)


@pytest.fixture(scope="session")
def schema_validator():
    return SchemaValidator()

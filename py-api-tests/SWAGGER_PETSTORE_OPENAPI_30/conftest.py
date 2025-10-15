import os
from pathlib import Path
import pytest
import yaml
import requests
from typing import Dict, Any


# Load configuration from YAML file
@pytest.fixture(scope='session')
def config():
    config_path = Path(__file__).parent / "config.yml"
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file '{config_path}' not found.")
    
    with config_path.open("r") as file:
        raw_config = yaml.safe_load(file)
    
    def resolve_env_var(value):
        if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
            env_var = value[2:-1]
            return os.getenv(env_var, "")
        return value

    def resolve_config(data):
        if isinstance(data, dict):
            return {key: resolve_config(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [resolve_config(item) for item in data]
        return resolve_env_var(data)

    return resolve_config(raw_config)


# API Helper class for requests
class ApiHelper:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    def make_request(self, endpoint, params=None, headers=None, method="GET"):
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        response = requests.request(method, url, headers=headers, params=params)
        response.raise_for_status()
        return response


@pytest.fixture(scope='session')
def api_helper(config):
    base_url = config.get("api", {}).get("host", "").strip()
    if not base_url:
        raise ValueError("Base URL is not configured in the YAML file.")
    return ApiHelper(base_url=base_url)


# API Client class
class ApiClient:
    def __init__(self, api_helper: ApiHelper):
        self.api_helper = api_helper

    def get(self, endpoint, headers=None, params=None):
        return self.api_helper.make_request(endpoint, params=params, headers=headers, method="GET")


@pytest.fixture(scope='session')
def api_client(api_helper):
    return ApiClient(api_helper)


# Fixtures for authentication and related data
@pytest.fixture(scope='session')
def valid_api_key(config):
    return config.get("authentication", {}).get("api_key")


@pytest.fixture(scope='session')
def invalid_api_key():
    return "invalid_api_key_123456"


@pytest.fixture(scope='session')
def oauth2_token(config):
    return config.get("authentication", {}).get("oauth2_token")


@pytest.fixture(scope='session')
def valid_location():
    return {"location": "test-location"}


# Schema Validator Class
class SchemaValidator:
    # Order schema validation
    def validate_order_schema(self, order_data: Dict[str, Any]) -> bool:
        """Validate Order object schema"""
        required_fields = ['id', 'petId', 'quantity', 'shipDate', 'status', 'complete']
        return all(field in order_data for field in required_fields)

    # Category schema validation
    def validate_category_schema(self, category_data: Dict[str, Any]) -> bool:
        """Validate Category object schema"""
        required_fields = ['id', 'name']
        return all(field in category_data for field in required_fields)

    # User schema validation
    def validate_user_schema(self, user_data: Dict[str, Any]) -> bool:
        """Validate User object schema"""
        required_fields = ['id', 'username', 'firstName', 'lastName', 'email', 'password', 'phone', 'userStatus']
        return all(field in user_data for field in required_fields)

    # Tag schema validation
    def validate_tag_schema(self, tag_data: Dict[str, Any]) -> bool:
        """Validate Tag object schema"""
        required_fields = ['id', 'name']
        return all(field in tag_data for field in required_fields)

    # Pet schema validation (includes nested validation for category and tags)
    def validate_pet_schema(self, pet_data: Dict[str, Any]) -> bool:
        """Validate Pet object schema"""
        required_fields = ['name', 'photoUrls']
        if not all(field in pet_data for field in required_fields):
            return False

        # Nested validation for category
        if "category" in pet_data:
            category_required_fields = ['id', 'name']
            if not all(field in pet_data["category"] for field in category_required_fields):
                return False

        # Nested validation for tags
        if "tags" in pet_data:
            for tag in pet_data["tags"]:
                tag_required_fields = ['id', 'name']
                if not all(field in tag for field in tag_required_fields):
                    return False
        
        return True

    # ApiResponse schema validation
    def validate_api_response_schema(self, response_data: Dict[str, Any]) -> bool:
        """Validate ApiResponse object schema"""
        required_fields = ['code', 'type', 'message']
        return all(field in response_data for field in required_fields)


@pytest.fixture(scope='session')
def schema_validator():
    return SchemaValidator()

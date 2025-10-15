import pytest
import requests
import yaml
import os
from pathlib import Path
from typing import Dict, Any


# Load configuration from YAML file
@pytest.fixture(scope="session")
def config():
    config_file = Path(__file__).parent / "config.yml"
    if not config_file.exists():
        raise FileNotFoundError(f"Config file not found: {config_file}")
    
    with open(config_file, "r") as file:
        config_data = yaml.safe_load(file)
    
    def resolve_env_variables(value):
        if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
            env_var = value[2:-1]
            return os.getenv(env_var, "")
        return value

    # Replace environment variable placeholders
    def recursive_resolve(data):
        if isinstance(data, dict):
            return {key: recursive_resolve(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [recursive_resolve(item) for item in data]
        else:
            return resolve_env_variables(data)

    return recursive_resolve(config_data)


# Helper class for making HTTP requests
@pytest.fixture(scope="session")
def api_helper(config):
    class ApiHelper:
        def __init__(self, base_url):
            self.base_url = base_url.strip()

        def make_request(self, endpoint, params=None, headers=None, method='GET'):
            url = f"{self.base_url}/{endpoint.lstrip('/')}"
            response = requests.request(method=method, url=url, params=params, headers=headers)
            return response

    return ApiHelper(config["api"]["host"])


# Simple API client
@pytest.fixture(scope="session")
def api_client(api_helper):
    class ApiClient:
        def get(self, endpoint, headers=None, params=None):
            return api_helper.make_request(endpoint, params=params, headers=headers, method='GET')

    return ApiClient()


# Fixtures for authentication and test data
@pytest.fixture(scope="session")
def valid_api_key(config):
    return config.get("authentication", {}).get("api_key", "")


@pytest.fixture(scope="session")
def invalid_api_key():
    return "invalid_api_key"


@pytest.fixture(scope="session")
def valid_location():
    return {"latitude": 37.7749, "longitude": -122.4194}


@pytest.fixture(scope="session")
def oauth2_token(config):
    return config.get("authentication", {}).get("oauth2_token", "")


# SchemaValidator class for schema validation
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
        top_level_valid = all(field in pet_data for field in required_fields)
        
        # Validate nested 'category' schema if present
        if 'category' in pet_data and pet_data['category']:
            category_validator = self.validate_category_schema(pet_data['category'])
        else:
            category_validator = True
        
        return top_level_valid and category_validator

    def validate_api_response_schema(self, api_response_data: Dict[str, Any]) -> bool:
        """Validate ApiResponse object schema"""
        required_fields = ['code', 'type', 'message']
        return all(field in api_response_data for field in required_fields)


@pytest.fixture(scope="session")
def schema_validator():
    return SchemaValidator()

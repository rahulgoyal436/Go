import os
import pytest
import requests
import yaml
from pathlib import Path
from typing import Dict, Any


# Fixture: Load configuration from YAML file
@pytest.fixture(scope="session")
def config():
    config_file = Path(__file__).parent / "config.yml"
    if not config_file.is_file():
        raise FileNotFoundError("Configuration file not found at: config.yml")
    with open(config_file, "r") as file:
        raw_config = yaml.safe_load(file)
    
    def replace_env_vars(value):
        if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
            env_var = value[2:-1]  # Extract variable name
            return os.getenv(env_var, "")
        return value

    def recursive_replace(obj):
        if isinstance(obj, dict):
            return {k: recursive_replace(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [recursive_replace(v) for v in obj]
        else:
            return replace_env_vars(obj)

    return recursive_replace(raw_config)


# Helper class for API requests
class APIHelper:
    def __init__(self, base_url):
        self.base_url = base_url.rstrip("/")

    def make_request(self, endpoint, params=None, headers=None, method="GET"):
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        response = requests.request(
            method=method.upper(),
            url=url,
            params=params,
            headers=headers
        )
        return response


@pytest.fixture(scope="session")
def api_helper(config):
    base_url = config["api"]["host"]
    return APIHelper(base_url)


# Simple API client for convenience
class APIClient:
    def __init__(self, api_helper):
        self.api_helper = api_helper

    def get(self, endpoint, headers=None, params=None):
        return self.api_helper.make_request(endpoint, headers=headers, params=params, method="GET")


@pytest.fixture(scope="session")
def api_client(api_helper):
    return APIClient(api_helper)


# Fixtures for authentication and test parameters
@pytest.fixture(scope="session")
def valid_api_key(config):
    return config.get("api", {}).get("valid_api_key")


@pytest.fixture(scope="session")
def invalid_api_key():
    return "invalid_api_key_12345"


@pytest.fixture(scope="session")
def valid_location():
    return "test-location"


@pytest.fixture(scope="session")
def oauth2_token(config):
    return config.get("api", {}).get("oauth2_token")


# SchemaValidator class for schema validation
class SchemaValidator:
    def validate_schema_order(self, order_data: Dict[str, Any]) -> bool:
        """Validate Order object schema"""
        required_fields = ['id', 'petId', 'quantity', 'shipDate', 'status', 'complete']
        return all(field in order_data for field in required_fields)

    def validate_schema_category(self, category_data: Dict[str, Any]) -> bool:
        """Validate Category object schema"""
        required_fields = ['id', 'name']
        return all(field in category_data for field in required_fields)

    def validate_schema_user(self, user_data: Dict[str, Any]) -> bool:
        """Validate User object schema"""
        required_fields = ['id', 'username', 'firstName', 'lastName', 'email', 'password', 'phone', 'userStatus']
        return all(field in user_data for field in required_fields)

    def validate_schema_tag(self, tag_data: Dict[str, Any]) -> bool:
        """Validate Tag object schema"""
        required_fields = ['id', 'name']
        return all(field in tag_data for field in required_fields)

    def validate_schema_pet(self, pet_data: Dict[str, Any]) -> bool:
        """Validate Pet object schema with nested validation"""
        required_fields = ['name', 'photoUrls']
        if not all(field in pet_data for field in required_fields):
            return False

        # Validate nested Category schema
        if "category" in pet_data:
            category_required_fields = ['id', 'name']
            category_data = pet_data["category"]
            if not all(field in category_data for field in category_required_fields):
                return False

        # Validate nested Tags schema
        if "tags" in pet_data:
            tags_data = pet_data["tags"]
            for tag in tags_data:
                tag_required_fields = ['id', 'name']
                if not all(field in tag for field in tag_required_fields):
                    return False

        return True

    def validate_schema_api_response(self, response_data: Dict[str, Any]) -> bool:
        """Validate ApiResponse object schema"""
        required_fields = ['code', 'type', 'message']
        return all(field in response_data for field in required_fields)


@pytest.fixture(scope="session")
def schema_validator():
    return SchemaValidator()

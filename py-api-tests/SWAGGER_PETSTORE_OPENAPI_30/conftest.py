import os
import pytest
import yaml
import requests
from pathlib import Path
from typing import Dict, Any


# Fixture: Load configuration from config.yml
@pytest.fixture(scope="session")
def config():
    config_path = Path(__file__).parent / "config.yml"
    try:
        with open(config_path, "r") as file:
            raw_config = yaml.safe_load(file)
    except FileNotFoundError:
        pytest.fail(f"Configuration file not found at {config_path}")
    except yaml.YAMLError as e:
        pytest.fail(f"Error parsing YAML configuration: {e}")

    def replace_env_vars(value):
        if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
            env_var = value[2:-1]
            return os.getenv(env_var, f"Environment variable '{env_var}' not set")
        return value

    def resolve_config(cfg):
        if isinstance(cfg, dict):
            return {k: resolve_config(v) for k, v in cfg.items()}
        elif isinstance(cfg, list):
            return [resolve_config(item) for item in cfg]
        else:
            return replace_env_vars(cfg)

    return resolve_config(raw_config)


# Helper class for making HTTP requests
class APIHelper:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    def make_request(self, endpoint, params=None, headers=None, method="GET"):
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        response = requests.request(method, url, params=params, headers=headers)
        return response


# Fixture: Provide the APIHelper instance
@pytest.fixture(scope="session")
def api_helper(config):
    base_url = config["api"]["host"]
    return APIHelper(base_url=base_url)


# Fixture: Simple API client with common methods
class APIClient:
    def __init__(self, api_helper: APIHelper):
        self.helper = api_helper

    def get(self, endpoint, headers=None, params=None):
        return self.helper.make_request(endpoint, params=params, headers=headers, method="GET")


@pytest.fixture(scope="session")
def api_client(api_helper):
    return APIClient(api_helper=api_helper)


# Fixture: Valid API key extraction
@pytest.fixture(scope="session")
def valid_api_key(config):
    return config["authentication"]["api_key"]


# Fixture: Invalid API key for testing
@pytest.fixture(scope="session")
def invalid_api_key():
    return "INVALID_API_KEY_12345"


# Fixture: Valid location parameter for testing
@pytest.fixture(scope="session")
def valid_location():
    return {"location": "New York"}


# Fixture: OAuth2 token extraction
@pytest.fixture(scope="session")
def oauth2_token(config):
    return config["authentication"]["petstore_auth"]


# Schema Validator Class
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

        # Validate nested "category" field
        if "category" in pet_data:
            required_category_fields = ['id', 'name']
            if not all(field in pet_data["category"] for field in required_category_fields):
                return False

        # Validate nested "tags" field
        if "tags" in pet_data:
            for tag in pet_data["tags"]:
                required_tag_fields = ['id', 'name']
                if not all(field in tag for field in required_tag_fields):
                    return False

        return True

    def validate_api_response_schema(self, api_response_data: Dict[str, Any]) -> bool:
        """Validate ApiResponse object schema"""
        required_fields = ['code', 'type', 'message']
        return all(field in api_response_data for field in required_fields)


@pytest.fixture(scope="session")
def schema_validator():
    return SchemaValidator()

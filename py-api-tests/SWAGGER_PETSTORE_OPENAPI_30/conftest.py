import pytest
import yaml
import os
import requests
from pathlib import Path
from typing import Dict, Any


# Load configuration fixture
@pytest.fixture(scope="session")
def config():
    config_path = Path(__file__).parent / "config.yml"
    try:
        with open(config_path, "r") as f:
            raw_config = yaml.safe_load(f)
    except FileNotFoundError:
        raise RuntimeError("Configuration file not found.")
    except yaml.YAMLError as e:
        raise RuntimeError(f"Error parsing the configuration file: {e}")

    def resolve_env_vars(value: str) -> str:
        if value.startswith("${") and value.endswith("}"):
            env_var = value[2:-1]
            return os.getenv(env_var, "")
        return value

    def resolve_env(config_dict: Dict[str, Any]) -> Dict[str, Any]:
        for key, val in config_dict.items():
            if isinstance(val, dict):
                config_dict[key] = resolve_env(val)
            elif isinstance(val, str):
                config_dict[key] = resolve_env_vars(val)
        return config_dict

    return resolve_env(raw_config)


# API Helper class for making HTTP requests
class ApiHelper:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    def make_request(self, endpoint: str, params=None, headers=None, method="GET"):
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        response = requests.request(method, url, params=params, headers=headers)
        return response


@pytest.fixture(scope="session")
def api_helper(config):
    if "api" not in config or "host" not in config["api"]:
        raise RuntimeError("API host not configured")
    return ApiHelper(base_url=config["api"]["host"])


# Simple API client
@pytest.fixture
def api_client(api_helper):
    class ApiClient:
        def get(self, endpoint: str, headers=None, params=None):
            return api_helper.make_request(endpoint, method="GET", headers=headers, params=params)

    return ApiClient()


# Valid API Key fixture
@pytest.fixture(scope="session")
def valid_api_key(config):
    if "authentication" not in config or "api_key" not in config["authentication"]:
        raise RuntimeError("API key not configured")
    return config["authentication"]["api_key"]


# Invalid API Key fixture
@pytest.fixture(scope="session")
def invalid_api_key():
    return "INVALID_API_KEY"


# Valid location fixture
@pytest.fixture(scope="session")
def valid_location():
    return {"latitude": 37.7749, "longitude": -122.4194}


# OAuth2 Token fixture
@pytest.fixture(scope="session")
def oauth2_token(config):
    if "authentication" not in config or "petstore_auth" not in config["authentication"]:
        raise RuntimeError("OAuth2 authentication token not configured")
    return config["authentication"]["petstore_auth"]


# Schema Validator class
class SchemaValidator:
    def validate_order_schema(self, order_data: Dict[str, Any]) -> bool:
        required_fields = ['id', 'petId', 'quantity', 'shipDate', 'status', 'complete']
        return all(field in order_data for field in required_fields)

    def validate_category_schema(self, category_data: Dict[str, Any]) -> bool:
        required_fields = ['id', 'name']
        return all(field in category_data for field in required_fields)

    def validate_user_schema(self, user_data: Dict[str, Any]) -> bool:
        required_fields = ['id', 'username', 'firstName', 'lastName', 'email', 'password', 'phone', 'userStatus']
        return all(field in user_data for field in required_fields)

    def validate_tag_schema(self, tag_data: Dict[str, Any]) -> bool:
        required_fields = ['id', 'name']
        return all(field in tag_data for field in required_fields)

    def validate_pet_schema(self, pet_data: Dict[str, Any]) -> bool:
        required_fields = ['name', 'photoUrls']
        if not all(field in pet_data for field in required_fields):
            return False
        if 'category' in pet_data and isinstance(pet_data['category'], dict):
            category_required_fields = ['id', 'name']
            if not all(field in pet_data['category'] for field in category_required_fields):
                return False
        if 'tags' in pet_data and isinstance(pet_data['tags'], list):
            for tag in pet_data['tags']:
                tag_required_fields = ['id', 'name']
                if not all(field in tag for field in tag_required_fields):
                    return False
        return True

    def validate_api_response_schema(self, api_response_data: Dict[str, Any]) -> bool:
        required_fields = ['code', 'type', 'message']
        return all(field in api_response_data for field in required_fields)


@pytest.fixture(scope="session")
def schema_validator():
    return SchemaValidator()

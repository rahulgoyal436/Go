import os
import yaml
import pytest
import requests
from pathlib import Path
from typing import Dict, Any


class APIHelper:
    def __init__(self, base_url: str):
        self.base_url = base_url.strip()

    def make_request(self, endpoint: str, params=None, headers=None, method="GET", data=None):
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        try:
            if method.upper() == "GET":
                response = requests.get(url, params=params, headers=headers)
            elif method.upper() == "POST":
                response = requests.post(url, json=data, headers=headers)
            elif method.upper() == "PUT":
                response = requests.put(url, json=data, headers=headers)
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            return response
        except requests.RequestException as e:
            raise RuntimeError(f"Request failed: {e}")


class APIClient:
    def __init__(self, api_helper: APIHelper):
        self.api_helper = api_helper

    def get(self, endpoint: str, headers=None, params=None):
        return self.api_helper.make_request(endpoint, params=params, headers=headers, method="GET")


class SchemaValidator:
    def validate_schema_order(self, order_data: Dict[str, Any]) -> bool:
        required_fields = ['id', 'petId', 'quantity', 'shipDate', 'status', 'complete']
        return all(field in order_data for field in required_fields)

    def validate_schema_category(self, category_data: Dict[str, Any]) -> bool:
        required_fields = ['id', 'name']
        return all(field in category_data for field in required_fields)

    def validate_schema_user(self, user_data: Dict[str, Any]) -> bool:
        required_fields = ['id', 'username', 'firstName', 'lastName', 'email', 'password', 'phone', 'userStatus']
        return all(field in user_data for field in required_fields)

    def validate_schema_tag(self, tag_data: Dict[str, Any]) -> bool:
        required_fields = ['id', 'name']
        return all(field in tag_data for field in required_fields)

    def validate_schema_pet(self, pet_data: Dict[str, Any]) -> bool:
        required_fields = ['name', 'photoUrls']
        is_valid = all(field in pet_data for field in required_fields)

        # Validate nested category
        if 'category' in pet_data:
            category_data = pet_data['category']
            is_valid &= self.validate_schema_category(category_data)

        # Validate nested tags
        if 'tags' in pet_data and isinstance(pet_data['tags'], list):
            for tag in pet_data['tags']:
                is_valid &= self.validate_schema_tag(tag)

        return is_valid

    def validate_schema_api_response(self, api_response_data: Dict[str, Any]) -> bool:
        required_fields = ['code', 'type', 'message']
        return all(field in api_response_data for field in required_fields)


@pytest.fixture(scope="session")
def config() -> Dict[str, Any]:
    config_path = Path(__file__).parent / 'config.yml'
    try:
        with open(config_path, 'r') as file:
            config_data = yaml.safe_load(file)

        def resolve_env_vars(value):
            if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
                env_var = value[2:-1]
                return os.getenv(env_var, None)
            return value

        # Resolve environment variables
        for key, value in config_data.items():
            if isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    config_data[key][sub_key] = resolve_env_vars(sub_value)
            else:
                config_data[key] = resolve_env_vars(value)

        return config_data

    except Exception as e:
        raise RuntimeError(f"Failed to load configuration: {e}")


@pytest.fixture(scope="session")
def api_helper(config) -> APIHelper:
    base_url = config['api']['host']
    if not base_url:
        raise ValueError("API base URL is not configured properly")
    return APIHelper(base_url)


@pytest.fixture(scope="session")
def api_client(api_helper) -> APIClient:
    return APIClient(api_helper)


@pytest.fixture(scope="session")
def schema_validator() -> SchemaValidator:
    return SchemaValidator()


@pytest.fixture(scope="session")
def valid_api_key(config) -> str:
    api_key = config['authentication']['api_key']
    if not api_key:
        raise ValueError("Valid API key is not configured properly")
    return api_key


@pytest.fixture(scope="session")
def invalid_api_key() -> str:
    return "invalid_api_key_for_testing"


@pytest.fixture(scope="session")
def valid_location() -> str:
    return "New York"


@pytest.fixture(scope="session")
def oauth2_token(config) -> str:
    token = config['authentication']['petstore_auth']
    if not token:
        raise ValueError("OAuth2 token is not configured properly")
    return token

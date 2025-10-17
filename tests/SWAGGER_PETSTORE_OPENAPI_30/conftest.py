import os
from pathlib import Path
import yaml
import pytest
import requests
from typing import Dict, Any


# ---- Config Fixture ----
@pytest.fixture(scope="session")
def config():
    """Load and parse configuration from the YAML file"""
    config_path = Path(__file__).parent / "config.yml"
    try:
        with config_path.open("r") as file:
            raw_config = yaml.safe_load(file)
    except FileNotFoundError:
        raise FileNotFoundError(f"Configuration file not found at {config_path}")
    except yaml.YAMLError as e:
        raise RuntimeError(f"Error parsing YAML configuration file: {e}")

    def replace_env_variables(value):
        if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
            env_var = value[2:-1]
            return os.getenv(env_var, None)
        return value

    return {
        key: {sub_key: replace_env_variables(sub_value) for sub_key, sub_value in sub_config.items()}
        for key, sub_config in raw_config.items()
    }


# ---- API Helper Fixture ----
class APIHelper:
    def __init__(self, base_url: str):
        self.base_url = base_url.strip()

    def make_request(self, endpoint: str, params=None, headers=None, method="GET"):
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        try:
            response = requests.request(method, url, params=params, headers=headers)
            response.raise_for_status()
        except requests.RequestException as e:
            raise RuntimeError(f"Error making API request: {e}")
        return response.json()


@pytest.fixture(scope="session")
def api_helper(config):
    base_url = config["api"]["host"]
    return APIHelper(base_url)


# ---- API Client Fixture ----
class APIClient:
    def __init__(self, api_helper: APIHelper):
        self.api_helper = api_helper

    def get(self, endpoint, headers=None, params=None):
        return self.api_helper.make_request(endpoint, params=params, headers=headers, method="GET")


@pytest.fixture(scope="session")
def api_client(api_helper):
    return APIClient(api_helper)


# ---- Authentication Fixtures ----
@pytest.fixture(scope="session")
def valid_api_key(config):
    return config["authentication"]["api_key"]


@pytest.fixture(scope="session")
def invalid_api_key():
    return "INVALID_API_KEY_TEST"


@pytest.fixture(scope="session")
def valid_location():
    return {"location": "test_location"}


@pytest.fixture(scope="session")
def oauth2_token(config):
    return config["authentication"]["petstore_auth"]


# ---- Schema Validator ----
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
        """Validate Pet object schema"""
        required_fields = ['name', 'photoUrls']
        if not all(field in pet_data for field in required_fields):
            return False
        if 'category' in pet_data and isinstance(pet_data['category'], dict):
            category_fields = ['id', 'name']
            if not all(field in pet_data['category'] for field in category_fields):
                return False
        return True

    def validate_schema_api_response(self, api_response_data: Dict[str, Any]) -> bool:
        """Validate ApiResponse object schema"""
        required_fields = ['code', 'type', 'message']
        return all(field in api_response_data for field in required_fields)


@pytest.fixture(scope="session")
def schema_validator():
    return SchemaValidator()

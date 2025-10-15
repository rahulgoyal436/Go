import pytest
import requests
import yaml
import os
from pathlib import Path
from typing import Dict, Any

# Load configuration from the YAML file
@pytest.fixture(scope="session")
def config():
    config_file_path = Path(__file__).parent / "config.yml"
    with open(config_file_path, "r") as file:
        config_data = yaml.safe_load(file)

    # Replace ${var} placeholders with environment values
    for key, value in config_data.items():
        if isinstance(value, dict):
            config_data[key] = {
                k: os.getenv(v[2:], v) if v.startswith("${") else v
                for k, v in value.items()
            }
        elif isinstance(value, str) and value.startswith("${"):
            config_data[key] = os.getenv(value[2:], value)

    return config_data


# Helper class for making HTTP requests
class APIHelper:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    def make_request(self, endpoint: str, params=None, headers=None, method="GET"):
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        response = requests.request(method=method, url=url, params=params, headers=headers)
        response.raise_for_status()
        return response


@pytest.fixture(scope="session")
def api_helper(config):
    base_url = config["api"]["host"]
    return APIHelper(base_url)


# API client class
class APIClient:
    def __init__(self, api_helper: APIHelper):
        self.api_helper = api_helper

    def get(self, endpoint: str, headers=None, params=None):
        return self.api_helper.make_request(endpoint, params=params, headers=headers, method="GET")


@pytest.fixture(scope="session")
def api_client(api_helper):
    return APIClient(api_helper)


# Valid API Key fixture
@pytest.fixture(scope="session")
def valid_api_key(config):
    return config["authentication"]["api_key"]


# Invalid API Key fixture
@pytest.fixture(scope="session")
def invalid_api_key():
    return "INVALID_API_KEY"


# Valid Location fixture
@pytest.fixture(scope="session")
def valid_location():
    return {"location": "12345"}  # Replace with actual test data as needed


# OAuth2 Token fixture
@pytest.fixture(scope="session")
def oauth2_token(config):
    return config["authentication"]["petstore_auth"]


# Schema validation functions
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

        if "category" in pet_data and isinstance(pet_data["category"], dict):
            category_required_fields = ['id', 'name']
            if not all(field in pet_data["category"] for field in category_required_fields):
                return False

        if "tags" in pet_data and isinstance(pet_data["tags"], list):
            for tag in pet_data["tags"]:
                tag_required_fields = ['id', 'name']
                if not all(field in tag for field in tag_required_fields):
                    return False

        return True

    def validate_api_response_schema(self, api_response_data: Dict[str, Any]) -> bool:
        """Validate ApiResponse object schema"""
        required_fields = ['code', 'type', 'message']
        return all(field in api_response_data for field in required_fields)


@pytest.fixture(scope="session")
def schema_validator():
    return SchemaValidator()

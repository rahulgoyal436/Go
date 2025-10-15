import os
import pytest
import requests
import yaml
from pathlib import Path
from typing import Dict, Any

# Load configuration fixture
@pytest.fixture(scope="session")
def config():
    config_path = Path(__file__).parent / "config.yml"
    try:
        with open(config_path, "r") as file:
            config_data = yaml.safe_load(file)
        for key, value in config_data.items():
            if isinstance(value, dict):
                for inner_key, inner_value in value.items():
                    if isinstance(inner_value, str) and inner_value.startswith("${") and inner_value.endswith("}"):
                        env_var = inner_value[2:-1]
                        config_data[key][inner_key] = os.environ.get(env_var, None)
        return config_data
    except Exception as e:
        pytest.fail(f"Unable to load configuration: {e}")


# Helper class for making HTTP requests
class ApiHelper:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    def make_request(self, endpoint: str, params=None, headers=None, method="GET"):
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        if method.upper() == "GET":
            return requests.get(url, params=params, headers=headers)
        elif method.upper() == "POST":
            return requests.post(url, json=params, headers=headers)
        elif method.upper() == "PUT":
            return requests.put(url, json=params, headers=headers)
        elif method.upper() == "DELETE":
            return requests.delete(url, headers=headers)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")


# Fixture for API helper
@pytest.fixture(scope="session")
def api_helper(config):
    return ApiHelper(base_url=config["api"]["host"])


# Simple API client fixture
class ApiClient:
    def __init__(self, api_helper):
        self.api_helper = api_helper

    def get(self, endpoint: str, headers=None, params=None):
        return self.api_helper.make_request(endpoint, params=params, headers=headers, method="GET")


@pytest.fixture(scope="session")
def api_client(api_helper):
    return ApiClient(api_helper)


# Fixture for valid API key
@pytest.fixture(scope="session")
def valid_api_key(config):
    return config["authentication"]["api_key"]


# Fixture for invalid API key
@pytest.fixture(scope="session")
def invalid_api_key():
    return "invalid_api_key"


# Fixture for valid location parameter
@pytest.fixture(scope="session")
def valid_location():
    return {"latitude": 37.7749, "longitude": -122.4194}  # Example location


# Fixture for OAuth2 token
@pytest.fixture(scope="session")
def oauth2_token(config):
    return config["authentication"]["petstore_auth"]


# Schemas validation functions
class SchemaValidator:
    @staticmethod
    def validate_order_schema(order_data: Dict[str, Any]) -> bool:
        required_fields = ["id", "petId", "quantity", "shipDate", "status", "complete"]
        return all(field in order_data for field in required_fields)

    @staticmethod
    def validate_category_schema(category_data: Dict[str, Any]) -> bool:
        required_fields = ["id", "name"]
        return all(field in category_data for field in required_fields)

    @staticmethod
    def validate_user_schema(user_data: Dict[str, Any]) -> bool:
        required_fields = [
            "id", "username", "firstName", "lastName", "email", "password",
            "phone", "userStatus"
        ]
        return all(field in user_data for field in required_fields)

    @staticmethod
    def validate_tag_schema(tag_data: Dict[str, Any]) -> bool:
        required_fields = ["id", "name"]
        return all(field in tag_data for field in required_fields)

    @staticmethod
    def validate_pet_schema(pet_data: Dict[str, Any]) -> bool:
        required_fields = ["name", "photoUrls"]
        return all(field in pet_data for field in required_fields)

    @staticmethod
    def validate_api_response_schema(api_response_data: Dict[str, Any]) -> bool:
        required_fields = ["code", "type", "message"]
        return all(field in api_response_data for field in required_fields)


@pytest.fixture(scope="session")
def schema_validator():
    return SchemaValidator()

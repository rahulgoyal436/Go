import os
import pytest
import requests
import yaml
from pathlib import Path
from typing import Dict, Any

# Load configuration from config.yml
@pytest.fixture(scope="session")
def config():
    config_file = Path(__file__).parent / "config.yml"
    if not config_file.exists():
        raise FileNotFoundError(f"Configuration file '{config_file}' not found.")
    with config_file.open("r") as file:
        content = yaml.safe_load(file)
        for key, value in content.items():
            if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
                env_var = value.strip("${}")
                content[key] = os.getenv(env_var, None)
    return content


# Helper class for making API requests
@pytest.fixture(scope="session")
def api_helper(config):
    class ApiHelper:
        def __init__(self, base_url):
            self.base_url = base_url.strip("/")

        def make_request(self, endpoint, params=None, headers=None, method="GET"):
            url = f"{self.base_url}/{endpoint.strip('/')}"
            response = requests.request(method, url, params=params, headers=headers)
            response.raise_for_status()
            return response

    return ApiHelper(base_url=config["api"]["host"])


# Simplified API client for common methods
@pytest.fixture(scope="session")
def api_client(api_helper):
    class ApiClient:
        def __init__(self, api_helper):
            self.api_helper = api_helper

        def get(self, endpoint, headers=None, params=None):
            return self.api_helper.make_request(endpoint, params=params, headers=headers, method="GET")

    return ApiClient(api_helper)


# Fixture for valid API key
@pytest.fixture
def valid_api_key(config):
    return config["authentication"]["api_key"]


# Fixture for invalid API key
@pytest.fixture
def invalid_api_key():
    return "INVALID_API_KEY"


# Fixture for providing a valid test location
@pytest.fixture
def valid_location():
    return {"lat": 40.7128, "lng": -74.0060}  # Example: New York coordinates


# Fixture for OAuth2 token
@pytest.fixture
def oauth2_token(config):
    return config["authentication"]["petstore_auth"]


# Dynamic SchemaValidator for component schemas
@pytest.fixture(scope="session")
def schema_validator():
    class SchemaValidator:
        def validate_schema_order(self, order_data: Dict[str, Any]) -> bool:
            """Validate Order object schema"""
            required_fields = ["id", "petId", "quantity", "shipDate", "status", "complete"]
            return all(field in order_data for field in required_fields)

        def validate_schema_category(self, category_data: Dict[str, Any]) -> bool:
            """Validate Category object schema"""
            required_fields = ["id", "name"]
            return all(field in category_data for field in required_fields)

        def validate_schema_user(self, user_data: Dict[str, Any]) -> bool:
            """Validate User object schema"""
            required_fields = ["id", "username", "firstName", "lastName", "email", "password", "phone", "userStatus"]
            return all(field in user_data for field in required_fields)

        def validate_schema_tag(self, tag_data: Dict[str, Any]) -> bool:
            """Validate Tag object schema"""
            required_fields = ["id", "name"]
            return all(field in tag_data for field in required_fields)

        def validate_schema_pet(self, pet_data: Dict[str, Any]) -> bool:
            """Validate Pet object schema"""
            required_fields = ["name", "photoUrls"]
            if not all(field in pet_data for field in required_fields):
                return False
            
            if "category" in pet_data:
                category_fields = ["id", "name"]
                if not all(field in pet_data["category"] for field in category_fields):
                    return False
            
            if "tags" in pet_data:
                for tag in pet_data["tags"]:
                    tag_fields = ["id", "name"]
                    if not all(field in tag for field in tag_fields):
                        return False
            
            return True

        def validate_schema_api_response(self, api_response: Dict[str, Any]) -> bool:
            """Validate ApiResponse object schema"""
            required_fields = ["code", "type", "message"]
            return all(field in api_response for field in required_fields)

    return SchemaValidator()

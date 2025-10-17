import os
import yaml
import pytest
import requests
from typing import Dict, Any
from pathlib import Path


# Load YAML configuration file
@pytest.fixture(scope="session")
def config():
    config_path = Path(__file__).parent / "config.yml"
    try:
        with open(config_path, "r") as file:
            raw_config = yaml.safe_load(file)
            for key, value in raw_config.get("api", {}).items():
                raw_config["api"][key] = value.replace("${var}", os.getenv(value.strip("${}"), ""))
            for key, value in raw_config.get("authentication", {}).items():
                raw_config["authentication"][key] = value.replace("${var}", os.getenv(value.strip("${}"), ""))
            return raw_config
    except FileNotFoundError:
        raise FileNotFoundError(f"Configuration file not found at {config_path}")
    except yaml.YAMLError:
        raise ValueError("Failed to parse the configuration file")


# Helper class for making API requests
class ApiHelper:
    def __init__(self, base_url: str):
        self.base_url = base_url.strip()

    def make_request(self, endpoint: str, params=None, headers=None, method="GET"):
        url = f"{self.base_url}{endpoint}"
        response = requests.request(method, url, params=params, headers=headers)
        return response


@pytest.fixture(scope="session")
def api_helper(config):
    base_url = config["api"]["host"]
    return ApiHelper(base_url)


# API client fixture for simple API calls
class ApiClient:
    def __init__(self, base_url: str):
        self.api_helper = ApiHelper(base_url)

    def get(self, endpoint: str, headers=None, params=None):
        return self.api_helper.make_request(endpoint, method="GET", headers=headers, params=params)


@pytest.fixture(scope="session")
def api_client(config):
    return ApiClient(config["api"]["host"])


# Valid API key fixture
@pytest.fixture(scope="session")
def valid_api_key(config):
    return config["authentication"]["api_key"]


# Invalid API key fixture
@pytest.fixture(scope="session")
def invalid_api_key():
    return "invalid_api_key_12345"


# Valid location fixture
@pytest.fixture(scope="session")
def valid_location():
    return {"latitude": 37.7749, "longitude": -122.4194}


# OAuth2 token fixture
@pytest.fixture(scope="session")
def oauth2_token(config):
    return config["authentication"]["petstore_auth"]


# Schema validator to dynamically validate schemas
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
        # Validate nested fields if required
        if "category" in pet_data:
            category_validator = SchemaValidator()
            if not category_validator.validate_schema_category(pet_data["category"]):
                return False
        if "tags" in pet_data:
            for tag in pet_data["tags"]:
                tag_validator = SchemaValidator()
                if not tag_validator.validate_schema_tag(tag):
                    return False
        return True

    def validate_schema_api_response(self, api_response_data: Dict[str, Any]) -> bool:
        """Validate ApiResponse object schema"""
        required_fields = ['code', 'type', 'message']
        return all(field in api_response_data for field in required_fields)


@pytest.fixture(scope="session")
def schema_validator():
    return SchemaValidator()

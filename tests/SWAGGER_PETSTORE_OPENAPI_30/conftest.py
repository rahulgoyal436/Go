import os
import pytest
import requests
import yaml
from pathlib import Path
from typing import Dict, Any

# Load configuration from YAML file
@pytest.fixture(scope="session")
def config():
    base_dir = Path(__file__).parent
    config_path = base_dir / "config.yml"
    
    try:
        with open(config_path, "r") as file:
            raw_config = yaml.safe_load(file)
            # Replace environment variable placeholders
            def replace_env_variables(value):
                if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
                    return os.getenv(value[2:-1], "")
                return value
            
            def resolve_placeholders(item):
                if isinstance(item, dict):
                    return {k: resolve_placeholders(v) for k, v in item.items()}
                elif isinstance(item, list):
                    return [resolve_placeholders(v) for v in item]
                return replace_env_variables(item)

            return resolve_placeholders(raw_config)
    except Exception as e:
        raise Exception(f"Failed to load config file: {e}")

# Helper class for making HTTP requests
class APIHelper:
    def __init__(self, base_url: str):
        self.base_url = base_url.strip()

    def make_request(self, endpoint: str, params=None, headers=None, method="GET") -> requests.Response:
        url = f"{self.base_url}/{endpoint.strip()}"
        try:
            if method.upper() == "GET":
                response = requests.get(url, params=params, headers=headers)
            elif method.upper() == "POST":
                response = requests.post(url, json=params, headers=headers)
            elif method.upper() == "PUT":
                response = requests.put(url, json=params, headers=headers)
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=headers)
            else:
                raise ValueError("Unsupported HTTP method")
            return response
        except Exception as e:
            raise Exception(f"Failed to make request to {url}: {e}")

# API helper fixture
@pytest.fixture(scope="session")
def api_helper(config):
    base_url = config["api"]["host"]
    return APIHelper(base_url)

# Simple API client
@pytest.fixture(scope="session")
def api_client(api_helper):
    class APIClient:
        def get(self, endpoint: str, headers=None, params=None) -> requests.Response:
            return api_helper.make_request(endpoint, params=params, headers=headers, method="GET")
        
    return APIClient()

# Fixture for valid API key
@pytest.fixture(scope="session")
def valid_api_key(config):
    return config["api"].get("valid_key")

# Fixture for invalid API key
@pytest.fixture(scope="session")
def invalid_api_key():
    return "INVALID_API_KEY"

# Fixture for valid location
@pytest.fixture(scope="session")
def valid_location():
    return {"location": "New York"}

# Fixture for OAuth2 token
@pytest.fixture(scope="session")
def oauth2_token(config):
    return config["api"].get("oauth2_token")

# Schema validation class
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
        # Validate nested category field
        if "category" in pet_data and pet_data["category"]:
            required_category_fields = ["id", "name"]
            if not all(field in pet_data["category"] for field in required_category_fields):
                return False
        # Validate nested tags field
        if "tags" in pet_data and pet_data["tags"]:
            required_tag_fields = ["id", "name"]
            for tag in pet_data["tags"]:
                if not all(field in tag for field in required_tag_fields):
                    return False
        return True

    def validate_schema_api_response(self, api_response_data: Dict[str, Any]) -> bool:
        """Validate ApiResponse object schema"""
        required_fields = ["code", "type", "message"]
        return all(field in api_response_data for field in required_fields)

# Fixture for schema validator
@pytest.fixture(scope="session")
def schema_validator():
    return SchemaValidator()

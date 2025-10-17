import pytest
import os
import yaml
import requests
from pathlib import Path
from typing import Dict, Any

# Helper function to load and extract environment variables from YAML config
def parse_config(yaml_content: dict) -> dict:
    def replace_env_var(value: str):
        if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
            return os.getenv(value[2:-1], "")
        return value

    def recursive_replace(data: dict):
        for key, value in data.items():
            if isinstance(value, dict):
                data[key] = recursive_replace(value)
            elif isinstance(value, list):
                data[key] = [replace_env_var(item) for item in value]
            else:
                data[key] = replace_env_var(value)
        return data

    return recursive_replace(yaml_content)


@pytest.fixture(scope="session")
def config():
    config_path = Path(__file__).parent / "config.yml"
    try:
        with open(config_path, "r") as file:
            yaml_content = yaml.safe_load(file)
            return parse_config(yaml_content)
    except FileNotFoundError:
        raise FileNotFoundError("Configuration file 'config.yml' not found.")
    except yaml.YAMLError as e:
        raise ValueError(f"Error parsing configuration file: {e}")


class APIHelper:
    def __init__(self, base_url: str):
        self.base_url = base_url.strip()

    def make_request(self, endpoint: str, params=None, headers=None, method="GET"):
        url = f"{self.base_url}/{endpoint}"
        try:
            response = requests.request(method, url, params=params, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise RuntimeError(f"Request failed: {e}")


@pytest.fixture(scope="session")
def api_helper(config):
    base_url = config.get("api", {}).get("host", "").strip()
    if not base_url:
        raise ValueError("API host URL is missing in the configuration.")
    return APIHelper(base_url)


class APIClient:
    def __init__(self, api_helper: APIHelper):
        self.api_helper = api_helper

    def get(self, endpoint: str, headers=None, params=None):
        return self.api_helper.make_request(endpoint, params=params, headers=headers, method="GET")


@pytest.fixture(scope="session")
def api_client(api_helper):
    return APIClient(api_helper)


@pytest.fixture(scope="session")
def valid_api_key(config):
    api_key = config.get("authentication", {}).get("api_key", "").strip()
    if not api_key:
        raise ValueError("Valid API key is missing in the configuration.")
    return api_key


@pytest.fixture(scope="session")
def invalid_api_key():
    return "invalid_api_key_123456"


@pytest.fixture(scope="session")
def valid_location():
    return {"latitude": "37.7749", "longitude": "-122.4194"}  # Example location for testing


@pytest.fixture(scope="session")
def oauth2_token(config):
    token = config.get("authentication", {}).get("petstore_auth", "").strip()
    if not token:
        raise ValueError("OAuth2 token is missing in the configuration.")
    return token


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
            category_data = pet_data["category"]
            if not self.validate_schema_category(category_data):
                return False
        if "tags" in pet_data:
            for tag in pet_data["tags"]:
                if not self.validate_schema_tag(tag):
                    return False
        return True

    def validate_schema_api_response(self, api_response_data: Dict[str, Any]) -> bool:
        """Validate ApiResponse object schema"""
        required_fields = ["code", "type", "message"]
        return all(field in api_response_data for field in required_fields)


@pytest.fixture(scope="session")
def schema_validator():
    return SchemaValidator()

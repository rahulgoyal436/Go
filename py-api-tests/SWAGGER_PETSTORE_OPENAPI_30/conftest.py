import os
import pytest
import yaml
import requests
from pathlib import Path
from typing import Dict, Any


# Fixture: Load configuration from config.yml file
@pytest.fixture(scope="session")
def config():
    config_path = Path(__file__).parent / "config.yml"
    with config_path.open("r") as f:
        cfg = yaml.safe_load(f)

    # Replace ${var} with environment variables
    for key, value in cfg.items():
        if isinstance(value, str) and "${" in value and "}" in value:
            env_var = value.strip("${}")
            cfg[key] = os.getenv(env_var, "")

    return cfg


# Helper class: For HTTP requests
class APIHelper:
    def __init__(self, base_url):
        self.base_url = base_url.rstrip('/')

    def make_request(self, endpoint, params=None, headers=None, method="GET"):
        url = f"{self.base_url}{endpoint}"
        method = method.lower()
        if method == "get":
            response = requests.get(url, params=params, headers=headers)
        elif method == "post":
            response = requests.post(url, json=params, headers=headers)
        elif method == "put":
            response = requests.put(url, json=params, headers=headers)
        elif method == "delete":
            response = requests.delete(url, headers=headers)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
        return response


# Fixture: API Helper
@pytest.fixture(scope="session")
def api_helper(config):
    return APIHelper(base_url=config["api"]["host"])


# Fixture: API Client
class APIClient:
    def __init__(self, api_helper):
        self.api_helper = api_helper

    def get(self, endpoint, headers=None, params=None):
        return self.api_helper.make_request(endpoint, params=params, headers=headers, method="GET")


@pytest.fixture(scope="session")
def api_client(api_helper):
    return APIClient(api_helper)


# Fixture: Valid API Key
@pytest.fixture(scope="session")
def valid_api_key(config):
    return config.get("authentication", {}).get("valid_api_key")


# Fixture: Invalid API Key
@pytest.fixture(scope="session")
def invalid_api_key():
    return "invalid_api_key_12345"


# Fixture: Valid Location
@pytest.fixture(scope="session")
def valid_location():
    return {"lat": 37.7749, "long": -122.4194}


# Fixture: OAuth2 Token
@pytest.fixture(scope="session")
def oauth2_token(config):
    return config.get("authentication", {}).get("oauth2_token")


# Schema Validator Class
class SchemaValidator:

    def validate_order(self, data: Dict[str, Any]) -> bool:
        required_fields = ['id', 'petId', 'quantity', 'shipDate', 'status', 'complete']
        return all(field in data for field in required_fields)

    def validate_category(self, data: Dict[str, Any]) -> bool:
        required_fields = ['id', 'name']
        return all(field in data for field in required_fields)

    def validate_user(self, data: Dict[str, Any]) -> bool:
        required_fields = ['id', 'username', 'firstName', 'lastName', 'email', 'password', 'phone', 'userStatus']
        return all(field in data for field in required_fields)

    def validate_tag(self, data: Dict[str, Any]) -> bool:
        required_fields = ['id', 'name']
        return all(field in data for field in required_fields)

    def validate_pet(self, data: Dict[str, Any]) -> bool:
        required_fields = ['name', 'photoUrls']
        top_level_valid = all(field in data for field in required_fields)
        if 'category' in data and data["category"]:
            category_fields = ['id', 'name']
            category_valid = all(field in data["category"] for field in category_fields)
        else:
            category_valid = True
        if 'tags' in data and isinstance(data["tags"], list):
            tags_valid = all(all(tag_field in tag for tag_field in ['id', 'name']) for tag in data["tags"])
        else:
            tags_valid = True
        return top_level_valid and category_valid and tags_valid

    def validate_api_response(self, data: Dict[str, Any]) -> bool:
        required_fields = ['code', 'type', 'message']
        return all(field in data for field in required_fields)


# Fixture: Schema Validator
@pytest.fixture(scope="session")
def schema_validator():
    return SchemaValidator()

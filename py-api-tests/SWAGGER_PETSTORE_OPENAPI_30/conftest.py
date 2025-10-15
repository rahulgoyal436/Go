import os
import pytest
import requests
import yaml
from pathlib import Path
from typing import Dict, Any


class APIHelper:
    """Helper class for making HTTP requests."""

    def __init__(self, base_url: str):
        self.base_url = base_url.strip()

    def make_request(self, endpoint: str, params=None, headers=None, method='GET'):
        url = f"{self.base_url}{endpoint}"
        response = requests.request(method, url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()


class APIClient:
    """Simple API Client for predefined HTTP methods."""

    def __init__(self, api_helper: APIHelper):
        self.api_helper = api_helper

    def get(self, endpoint: str, headers=None, params=None):
        return self.api_helper.make_request(endpoint, params=params, headers=headers, method='GET')


def load_config():
    """Load config.yml file and replace ${var} with values from environment variables."""
    config_path = Path(__file__).parent / "config.yml"
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file {config_path} not found.")

    with config_path.open("r") as file:
        raw_config = yaml.safe_load(file)

    def replace_env_variables(value):
        if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
            env_var = value[2:-1]
            return os.getenv(env_var, None)
        return value

    def parse_config(data):
        if isinstance(data, dict):
            return {key: parse_config(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [parse_config(item) for item in data]
        else:
            return replace_env_variables(data)

    return parse_config(raw_config)


@pytest.fixture(scope="session")
def config():
    """Fixture to load configuration."""
    return load_config()


@pytest.fixture(scope="session")
def api_helper(config):
    """Fixture for the APIHelper class."""
    base_url = config.get("api", {}).get("host", "").strip()
    if not base_url:
        raise ValueError("API base URL is missing in the configuration.")
    return APIHelper(base_url)


@pytest.fixture(scope="session")
def api_client(api_helper):
    """Fixture for the APIClient class."""
    return APIClient(api_helper)


@pytest.fixture(scope="session")
def valid_api_key(config):
    """Fixture for valid API key."""
    api_key = config.get("authentication", {}).get("api_key", "").strip()
    if not api_key:
        raise ValueError("Valid API key is missing in the configuration.")
    return api_key


@pytest.fixture(scope="session")
def invalid_api_key():
    """Fixture for an invalid API key."""
    return "INVALID_API_KEY"


@pytest.fixture(scope="session")
def valid_location():
    """Fixture for a valid test location."""
    return {"location": "test-location"}


@pytest.fixture(scope="session")
def oauth2_token(config):
    """Fixture for extracting OAuth2 token."""
    token = config.get("authentication", {}).get("petstore_auth", "").strip()
    if not token:
        raise ValueError("OAuth2 token is missing in the configuration.")
    return token


class SchemaValidator:
    """Class for dynamically generating schema validation methods."""

    def __init__(self, components: Dict[str, Any]):
        self.components = components

    def generate_validation_method(self, schema_name: str, schema_content: Dict[str, Any]):
        def validate_method(data: Dict[str, Any]) -> bool:
            """Generated schema validation method."""
            required_fields = schema_content.get("required", list(schema_content.get("properties", {}).keys()))
            return all(field in data for field in required_fields)
        return validate_method


def load_components():
    """Load component schema and generate validation methods."""
    components = {
        "Order": {
            "properties": {
                "id": {"type": "integer", "format": "int64"},
                "petId": {"type": "integer", "format": "int64"},
                "quantity": {"type": "integer", "format": "int32"},
                "shipDate": {"type": "string", "format": "date-time"},
                "status": {"type": "string"},
                "complete": {"type": "boolean"},
            }
        },
        "Category": {
            "properties": {
                "id": {"type": "integer", "format": "int64"},
                "name": {"type": "string"},
            }
        },
        "User": {
            "properties": {
                "id": {"type": "integer", "format": "int64"},
                "username": {"type": "string"},
                "firstName": {"type": "string"},
                "lastName": {"type": "string"},
                "email": {"type": "string"},
                "password": {"type": "string"},
                "phone": {"type": "string"},
                "userStatus": {"type": "integer", "format": "int32"},
            }
        },
        "Tag": {
            "properties": {
                "id": {"type": "integer", "format": "int64"},
                "name": {"type": "string"},
            }
        },
        "Pet": {
            "required": ["name", "photoUrls"],
            "properties": {
                "id": {"type": "integer", "format": "int64"},
                "name": {"type": "string"},
                "photoUrls": {"type": "array"},
                "tags": {"type": "array"},
                "status": {"type": "string"},
            }
        },
        "ApiResponse": {
            "properties": {
                "code": {"type": "integer", "format": "int32"},
                "type": {"type": "string"},
                "message": {"type": "string"},
            }
        },
    }
    return components


@pytest.fixture(scope="session")
def schema_validator():
    """Fixture for SchemaValidator."""
    components = load_components()
    validator = SchemaValidator(components)

    for schema_name, schema_content in components.items():
        validate_method = validator.generate_validation_method(schema_name, schema_content)
        setattr(validator, f"validate_{schema_name.lower()}_schema", validate_method)

    return validator

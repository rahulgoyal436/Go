import os
import pytest
import requests
import yaml
from pathlib import Path
from typing import Any, Dict, Optional

@pytest.fixture(scope="session")
def config() -> Dict[str, Any]:
    """Load YAML configuration and substitute environment variables."""
    config_path = Path(__file__).parent / "config.yml"
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found at {config_path}")
    
    with open(config_path, "r") as file:
        raw_config = yaml.safe_load(file)
    
    def substitute_env_vars(item):
        if isinstance(item, str) and item.startswith("${") and item.endswith("}"):
            env_var = item[2:-1]
            return os.getenv(env_var, f"Missing env var: {env_var}")
        elif isinstance(item, dict):
            return {k: substitute_env_vars(v) for k, v in item.items()}
        elif isinstance(item, list):
            return [substitute_env_vars(i) for i in item]
        return item

    return substitute_env_vars(raw_config)


class ApiHelper:
    """Helper class for making HTTP requests."""
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    def make_request(self, endpoint: str, params=None, headers=None, method="GET"):
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        response = requests.request(method=method, url=url, params=params, headers=headers)
        return response


@pytest.fixture(scope="session")
def api_helper(config) -> ApiHelper:
    """Provide an API Helper instance."""
    return ApiHelper(base_url=config["api"]["host"])


class ApiClient:
    """Simple API client for specific operations."""
    def __init__(self, api_helper: ApiHelper):
        self.api_helper = api_helper

    def get(self, endpoint: str, headers: Optional[Dict[str, str]] = None, params: Optional[Dict[str, str]] = None):
        return self.api_helper.make_request(endpoint=endpoint, params=params, headers=headers, method="GET")


@pytest.fixture(scope="session")
def api_client(api_helper) -> ApiClient:
    """Provide an API Client instance."""
    return ApiClient(api_helper=api_helper)


@pytest.fixture(scope="session")
def valid_api_key(config) -> str:
    """Extract valid API key from configuration."""
    return config["authentication"]["api_key"]


@pytest.fixture(scope="session")
def invalid_api_key() -> str:
    """Provide a dummy invalid API key."""
    return "INVALID_API_KEY"


@pytest.fixture(scope="session")
def valid_location() -> str:
    """Provide a test location parameter."""
    return "test_location"


@pytest.fixture(scope="session")
def oauth2_token(config) -> str:
    """Extract OAuth2 token from configuration."""
    return config["authentication"]["petstore_auth"]


class SchemaValidator:
    """A dynamic schema validation class."""

    def validate_order_schema(self, order_data: Dict[str, Any]) -> bool:
        """Validate Order object schema."""
        required_fields = ['id', 'petId', 'quantity', 'shipDate', 'status', 'complete']
        return all(field in order_data for field in required_fields)

    def validate_category_schema(self, category_data: Dict[str, Any]) -> bool:
        """Validate Category object schema."""
        required_fields = ['id', 'name']
        return all(field in category_data for field in required_fields)

    def validate_user_schema(self, user_data: Dict[str, Any]) -> bool:
        """Validate User object schema."""
        required_fields = ['id', 'username', 'firstName', 'lastName', 'email', 'password', 'phone', 'userStatus']
        return all(field in user_data for field in required_fields)

    def validate_tag_schema(self, tag_data: Dict[str, Any]) -> bool:
        """Validate Tag object schema."""
        required_fields = ['id', 'name']
        return all(field in tag_data for field in required_fields)

    def validate_pet_schema(self, pet_data: Dict[str, Any]) -> bool:
        """Validate Pet object schema."""
        required_fields = ['name', 'photoUrls']
        nested_category_validator = self.validate_category_schema if "category" in pet_data else lambda x: True
        nested_tags_validator = all(self.validate_tag_schema(tag) for tag in pet_data.get("tags", []))
        return all(field in pet_data for field in required_fields) and nested_category_validator(pet_data.get("category", {})) and nested_tags_validator

    def validate_api_response_schema(self, api_response_data: Dict[str, Any]) -> bool:
        """Validate ApiResponse object schema."""
        required_fields = ['code', 'type', 'message']
        return all(field in api_response_data for field in required_fields)


@pytest.fixture(scope="session")
def schema_validator() -> SchemaValidator:
    """Provide a Schema Validator instance."""
    return SchemaValidator()

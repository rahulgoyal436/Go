import os
import pytest
import requests
import yaml
from pathlib import Path
from typing import Dict, Any

# Load configuration from YAML file
@pytest.fixture(scope="session")
def config() -> Dict[str, Any]:
    """Load API configuration from YAML file and replace ${var} with env values."""
    try:
        config_path = Path(__file__).parent / "config.yml"
        with open(config_path, "r") as file:
            config_data = yaml.safe_load(file)

        def resolve_env_var(value):
            if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
                env_var = value.strip("${").strip("}")
                return os.getenv(env_var, "")
            return value

        def replace_vars(data: Any):
            if isinstance(data, dict):
                return {k: replace_vars(v) for k, v in data.items()}
            elif isinstance(data, list):
                return [replace_vars(item) for item in data]
            else:
                return resolve_env_var(data)

        return replace_vars(config_data)

    except FileNotFoundError:
        pytest.exit("Configuration file not found. Please ensure config.yml exists.")
    except Exception as e:
        pytest.exit(f"Error loading configuration file: {str(e)}")


# Helper class for making HTTP requests
class APIHelper:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    def make_request(self, endpoint, params=None, headers=None, method='GET') -> requests.Response:
        """Make API request."""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        try:
            if method == "GET":
                response = requests.get(url, params=params, headers=headers)
            elif method == "POST":
                response = requests.post(url, json=params, headers=headers)
            elif method == "PUT":
                response = requests.put(url, json=params, headers=headers)
            elif method == "DELETE":
                response = requests.delete(url, headers=headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            return response
        except requests.RequestException as e:
            raise RuntimeError(f"API request failed: {str(e)}")


@pytest.fixture(scope="session")
def api_helper(config):
    """Provide APIHelper instance to tests."""
    base_url = config.get("api", {}).get("host", "").strip()
    if not base_url:
        pytest.exit("Base URL is missing in configuration.")
    return APIHelper(base_url)


# API client with convenience methods
class APIClient:
    def __init__(self, api_helper: APIHelper):
        self.api_helper = api_helper

    def get(self, endpoint, headers=None, params=None):
        return self.api_helper.make_request(endpoint, params=params, headers=headers, method="GET")

    def post(self, endpoint, headers=None, params=None):
        return self.api_helper.make_request(endpoint, params=params, headers=headers, method="POST")


@pytest.fixture(scope="session")
def api_client(api_helper):
    """Provide APIClient instance to tests."""
    return APIClient(api_helper)


@pytest.fixture(scope="session")
def valid_api_key(config):
    """Extract valid API key from configuration."""
    return config.get("api", {}).get("api_key", "")


@pytest.fixture(scope="session")
def invalid_api_key():
    """Provide an invalid API key."""
    return "INVALID_API_KEY"


@pytest.fixture(scope="session")
def valid_location():
    """Provide test location."""
    return "New York, NY"


@pytest.fixture(scope="session")
def oauth2_token(config):
    """Extract OAuth2 token from configuration."""
    return config.get("api", {}).get("oauth2_token", "")


# Dynamic schema validation class
class SchemaValidator:
    def validate_schema_order(self, order_data: Dict[str, Any]) -> bool:
        """Validate Order object schema"""
        required_fields = ['id', 'petId', 'quantity', 'shipDate', 'status', 'complete']
        return all(field in order_data for field in required_fields)

    def validate_schema_pet(self, pet_data: Dict[str, Any]) -> bool:
        """Validate Pet object schema"""
        required_fields = ['id', 'name', 'category', 'photoUrls', 'tags', 'status']
        return all(field in pet_data for field in required_fields)


@pytest.fixture(scope="session")
def schema_validator():
    """Provide SchemaValidator instance to tests."""
    return SchemaValidator()

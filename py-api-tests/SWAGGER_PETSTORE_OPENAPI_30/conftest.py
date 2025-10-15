import pytest
import requests
import yaml
import os
from pathlib import Path
from typing import Dict, Any


# Helper class for making HTTP requests
class ApiHelper:
    def __init__(self, base_url):
        self.base_url = base_url.strip()

    def make_request(self, endpoint, params=None, headers=None, method="GET"):
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
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
                raise ValueError(f"Unsupported HTTP method: {method}")
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"API request failed: {e}")


# Helper class for validation of schemas
class SchemaValidator:
    def validate_order_schema(self, order_data: Dict[str, Any]) -> bool:
        """Validate Order object schema."""
        required_fields = ["id", "petId", "quantity", "shipDate", "status", "complete"]
        return all(field in order_data for field in required_fields)

    def validate_category_schema(self, category_data: Dict[str, Any]) -> bool:
        """Validate Category object schema."""
        required_fields = ["id", "name"]
        return all(field in category_data for field in required_fields)

    def validate_user_schema(self, user_data: Dict[str, Any]) -> bool:
        """Validate User object schema."""
        required_fields = ["id", "username", "firstName", "lastName", "email", "password", "phone", "userStatus"]
        return all(field in user_data for field in required_fields)

    def validate_tag_schema(self, tag_data: Dict[str, Any]) -> bool:
        """Validate Tag object schema."""
        required_fields = ["id", "name"]
        return all(field in tag_data for field in required_fields)

    def validate_pet_schema(self, pet_data: Dict[str, Any]) -> bool:
        """Validate Pet object schema."""
        required_fields = ["name", "photoUrls"]
        if not all(field in pet_data for field in required_fields):
            return False
        # Additional nested validations
        category_data = pet_data.get("category", {})
        tag_data_list = pet_data.get("tags", [])
        if "category" in category_data:
            if not self.validate_category_schema(category_data):
                return False
        for tag_data in tag_data_list:
            if not self.validate_tag_schema(tag_data):
                return False
        return True

    def validate_api_response_schema(self, api_response: Dict[str, Any]) -> bool:
        """Validate ApiResponse object schema."""
        required_fields = ["code", "type", "message"]
        return all(field in api_response for field in required_fields)


@pytest.fixture(scope="session")
def config():
    """Load configuration from `config.yml` file."""
    config_path = Path(__file__).parent / "config.yml"
    try:
        with open(config_path, "r") as file:
            raw_config = yaml.safe_load(file)
        # Replace ${var} with environment variables
        def replace_env_vars(d):
            for key, value in d.items():
                if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
                    env_var = value[2:-1]
                    d[key] = os.getenv(env_var, "")
                elif isinstance(value, dict):
                    replace_env_vars(value)

        replace_env_vars(raw_config)
        return raw_config
    except FileNotFoundError:
        raise FileNotFoundError("Configuration file `config.yml` not found.")
    except yaml.YAMLError as e:
        raise RuntimeError(f"Error parsing configuration file: {e}")


@pytest.fixture(scope="session")
def api_helper(config):
    """Provide initialized API helper."""
    base_url = config["api"]["host"]
    return ApiHelper(base_url)


@pytest.fixture(scope="session")
def api_client(api_helper):
    """Provide a simple API client."""
    class ApiClient:
        def __init__(self, helper):
            self.helper = helper

        def get(self, endpoint, headers=None, params=None):
            return self.helper.make_request(endpoint=endpoint, headers=headers, params=params, method="GET")

    return ApiClient(api_helper)


@pytest.fixture(scope="session")
def valid_api_key(config):
    """Provide a valid API key."""
    return config.get("authentication", {}).get("apiKey")


@pytest.fixture(scope="session")
def invalid_api_key():
    """Provide an invalid API key."""
    return "INVALID_API_KEY"


@pytest.fixture(scope="session")
def valid_location():
    """Provide a valid test location parameter."""
    return {"location": "Test_Location"}


@pytest.fixture(scope="session")
def oauth2_token(config):
    """Provide OAuth2 token."""
    return config.get("authentication", {}).get("oauth2Token")


@pytest.fixture(scope="session")
def schema_validator():
    """Provide schema validation helper."""
    return SchemaValidator()

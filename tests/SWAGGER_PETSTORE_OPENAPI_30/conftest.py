import pytest
import os
import yaml
import requests
from pathlib import Path
from typing import Dict, Any


# Helper function to load configuration
def load_config():
    config_path = Path(__file__).parent / "config.yml"
    try:
        with config_path.open() as stream:
            config_data = yaml.safe_load(stream)
        for key, value in config_data.items():
            if isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    if isinstance(sub_value, str) and sub_value.startswith("${") and sub_value.endswith("}"):
                        env_var = sub_value[2:-1]
                        config_data[key][sub_key] = os.getenv(env_var, None)
        return config_data
    except FileNotFoundError:
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    except yaml.YAMLError as exc:
        raise RuntimeError(f"Error parsing YAML file: {exc}")


# Schema Validator Class
class SchemaValidator:
    def validate_schema_order(self, order_data: Dict[str, Any]) -> bool:
        """Validate Order schema"""
        required_fields = ['id', 'petId', 'quantity', 'shipDate', 'status', 'complete']
        return all(field in order_data for field in required_fields)

    def validate_schema_category(self, category_data: Dict[str, Any]) -> bool:
        """Validate Category schema"""
        required_fields = ['id', 'name']
        return all(field in category_data for field in required_fields)

    def validate_schema_user(self, user_data: Dict[str, Any]) -> bool:
        """Validate User schema"""
        required_fields = ['id', 'username', 'firstName', 'lastName', 'email', 'password', 'phone', 'userStatus']
        return all(field in user_data for field in required_fields)

    def validate_schema_tag(self, tag_data: Dict[str, Any]) -> bool:
        """Validate Tag schema"""
        required_fields = ['id', 'name']
        return all(field in tag_data for field in required_fields)

    def validate_schema_pet(self, pet_data: Dict[str, Any]) -> bool:
        """Validate Pet schema"""
        required_fields = ['name', 'photoUrls']
        if not all(field in pet_data for field in required_fields):
            return False
        if 'category' in pet_data:
            category_required_fields = ['id', 'name']
            if not all(field in pet_data['category'] for field in category_required_fields):
                return False
        if 'tags' in pet_data:
            for tag in pet_data.get('tags', []):
                tag_required_fields = ['id', 'name']
                if not all(field in tag for field in tag_required_fields):
                    return False
        return True

    def validate_schema_apiresponse(self, response_data: Dict[str, Any]) -> bool:
        """Validate ApiResponse schema"""
        required_fields = ['code', 'type', 'message']
        return all(field in response_data for field in required_fields)


# Helper Class for HTTP Requests
class ApiHelper:
    def __init__(self, base_url: str):
        self.base_url = base_url.strip()

    def make_request(self, endpoint, params=None, headers=None, method='GET'):
        url = f"{self.base_url}{endpoint}"
        try:
            if method.upper() == 'GET':
                response = requests.get(url, params=params, headers=headers)
            elif method.upper() == 'POST':
                response = requests.post(url, json=params, headers=headers)
            elif method.upper() == 'PUT':
                response = requests.put(url, json=params, headers=headers)
            elif method.upper() == 'DELETE':
                response = requests.delete(url, headers=headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise RuntimeError(f"HTTP request failed: {e}")


# Fixtures
@pytest.fixture(scope="session")
def config():
    return load_config()


@pytest.fixture(scope="session")
def api_helper(config):
    base_url = config['api']['host']
    return ApiHelper(base_url)


@pytest.fixture(scope="session")
def api_client(api_helper):
    class ApiClient:
        def __init__(self, helper: ApiHelper):
            self.helper = helper

        def get(self, endpoint, headers=None, params=None):
            """Make a GET request"""
            return self.helper.make_request(endpoint, params=params, headers=headers, method='GET')

    return ApiClient(api_helper)


@pytest.fixture(scope="session")
def valid_api_key(config):
    return config['authentication']['api_key']


@pytest.fixture(scope="session")
def invalid_api_key():
    return "invalid_api_key_12345"


@pytest.fixture(scope="session")
def valid_location():
    return {"latitude": 37.7749, "longitude": -122.4194}  # Example location (San Francisco coordinates)


@pytest.fixture(scope="session")
def oauth2_token(config):
    return config['authentication']['petstore_auth']


@pytest.fixture(scope="session")
def schema_validator():
    return SchemaValidator()

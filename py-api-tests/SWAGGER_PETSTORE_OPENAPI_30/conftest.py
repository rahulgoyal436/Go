import pytest
import requests
import yaml
import os
from pathlib import Path
from typing import Dict, Any

# Helper Class for API Requests
class APIHelper:
    def __init__(self, base_url: str):
        self.base_url = base_url.strip()

    def make_request(self, endpoint: str, params=None, headers=None, method='GET'):
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
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
            return response
        except requests.RequestException as e:
            raise RuntimeError(f"Request failed: {e}")

# Helper Class for Schema Validation
class SchemaValidator:
    def validate_order_schema(self, order_data: Dict[str, Any]) -> bool:
        """Validate Order object schema"""
        required_fields = ['id', 'petId', 'quantity', 'shipDate', 'status', 'complete']
        return all(field in order_data for field in required_fields)

    def validate_category_schema(self, category_data: Dict[str, Any]) -> bool:
        """Validate Category object schema"""
        required_fields = ['id', 'name']
        return all(field in category_data for field in required_fields)

    def validate_user_schema(self, user_data: Dict[str, Any]) -> bool:
        """Validate User object schema"""
        required_fields = ['id', 'username', 'firstName', 'lastName', 'email', 'password', 'phone', 'userStatus']
        return all(field in user_data for field in required_fields)

    def validate_tag_schema(self, tag_data: Dict[str, Any]) -> bool:
        """Validate Tag object schema"""
        required_fields = ['id', 'name']
        return all(field in tag_data for field in required_fields)

    def validate_pet_schema(self, pet_data: Dict[str, Any]) -> bool:
        """Validate Pet object schema"""
        required_fields = ['name', 'photoUrls']
        if not all(field in pet_data for field in required_fields):
            return False
        if 'category' in pet_data:
            category_data = pet_data.get('category', {})
            if not self.validate_category_schema(category_data):
                return False
        if 'tags' in pet_data:
            tags_data = pet_data.get('tags', [])
            for tag in tags_data:
                if not self.validate_tag_schema(tag):
                    return False
        return True

    def validate_api_response_schema(self, response_data: Dict[str, Any]) -> bool:
        """Validate ApiResponse object schema"""
        required_fields = ['code', 'type', 'message']
        return all(field in response_data for field in required_fields)

# Fixture Definitions
@pytest.fixture(scope='session')
def config():
    """Load configuration from YAML file"""
    config_path = Path(__file__).parent / "config.yml"
    try:
        with open(config_path, 'r') as file:
            raw_config = yaml.safe_load(file)
    except FileNotFoundError:
        raise FileNotFoundError(f"Configuration file {config_path} not found.")
    except yaml.YAMLError as e:
        raise RuntimeError(f"Error loading the YAML configuration file: {e}")

    # Replace environment variable placeholders
    def replace_env_vars(value):
        if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
            env_var = value[2:-1]
            return os.getenv(env_var, "")
        return value

    processed_config = {key: replace_env_vars(value) for key, value in raw_config.items() if isinstance(value, str) or not isinstance(value, dict)}
    return processed_config

@pytest.fixture
def api_helper(config):
    """Provide APIHelper instance"""
    base_url = config.get('api', {}).get('host', '')
    if not base_url:
        raise ValueError("Base URL is not properly configured in 'config.yml'.")
    return APIHelper(base_url)

@pytest.fixture
def api_client(api_helper):
    """Provide simple APIClient with 'get' method"""
    class APIClient:
        def __init__(self, helper: APIHelper):
            self.helper = helper

        def get(self, endpoint, headers=None, params=None):
            return self.helper.make_request(endpoint, params=params, headers=headers, method='GET')

    return APIClient(api_helper)

@pytest.fixture
def valid_api_key(config):
    """Provide valid API key from config"""
    return config.get('authentication', {}).get('apiKey', '')

@pytest.fixture
def invalid_api_key():
    """Provide invalid API key"""
    return "INVALID_API_KEY"

@pytest.fixture
def valid_location():
    """Provide valid location parameter for testing"""
    return "San Francisco"

@pytest.fixture
def oauth2_token(config):
    """Provide OAuth2 token from config"""
    return config.get('authentication', {}).get('oauthToken', '')

@pytest.fixture
def schema_validator():
    """Provide SchemaValidator instance"""
    return SchemaValidator()

import pytest
import requests
import yaml
import os
from pathlib import Path
from typing import Any, Dict

class APIHelper:
    def __init__(self, base_url: str):
        self.base_url = base_url.strip()

    def make_request(self, endpoint: str, params=None, headers=None, method='GET'):
        url = f"{self.base_url}{endpoint}"
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

class SchemaValidator:
    def validate_schema_order(self, order_data: Dict[str, Any]) -> bool:
        """Validate Order object schema."""
        required_fields = ['id', 'petId', 'quantity', 'shipDate', 'status', 'complete']
        return all(field in order_data for field in required_fields)
    
    def validate_schema_category(self, category_data: Dict[str, Any]) -> bool:
        """Validate Category object schema."""
        required_fields = ['id', 'name']
        return all(field in category_data for field in required_fields)
    
    def validate_schema_user(self, user_data: Dict[str, Any]) -> bool:
        """Validate User object schema."""
        required_fields = ['id', 'username', 'firstName', 'lastName', 'email', 'password', 'phone', 'userStatus']
        return all(field in user_data for field in required_fields)
    
    def validate_schema_tag(self, tag_data: Dict[str, Any]) -> bool:
        """Validate Tag object schema."""
        required_fields = ['id', 'name']
        return all(field in tag_data for field in required_fields)
    
    def validate_schema_pet(self, pet_data: Dict[str, Any]) -> bool:
        """Validate Pet object schema."""
        required_fields = ['name', 'photoUrls']
        if not all(field in pet_data for field in required_fields):
            return False
        category_required_fields = ['id', 'name']
        if 'category' in pet_data:
            if not all(field in pet_data['category'] for field in category_required_fields):
                return False
        for tag in pet_data.get('tags', []):
            tag_required_fields = ['id', 'name']
            if not all(field in tag for field in tag_required_fields):
                return False
        return True
    
    def validate_schema_api_response(self, response_data: Dict[str, Any]) -> bool:
        """Validate ApiResponse object schema."""
        required_fields = ['code', 'type', 'message']
        return all(field in response_data for field in required_fields)

@pytest.fixture(scope="session")
def config():
    config_file = Path(__file__).parent / "config.yml"
    if not config_file.exists():
        raise FileNotFoundError("Configuration file config.yml not found!")
    
    with config_file.open("r") as file:
        raw_config = yaml.safe_load(file)
    
    def resolve_env_vars(value: str):
        if value.startswith("${") and value.endswith("}"):
            env_var = value[2:-1]
            return os.getenv(env_var, "")
        return value
    
    def parse_nested(data):
        if isinstance(data, dict):
            return {k: parse_nested(resolve_env_vars(v)) if isinstance(v, str) else parse_nested(v) for k, v in data.items()}
        return data
    
    return parse_nested(raw_config)

@pytest.fixture(scope="session")
def api_helper(config):
    base_url = config.get('api', {}).get('host')
    if not base_url:
        raise ValueError("API host URL is not set in the configuration.")
    return APIHelper(base_url)

@pytest.fixture(scope="session")
def api_client(api_helper):
    class APIClient:
        def __init__(self, api_helper):
            self.api_helper = api_helper

        def get(self, endpoint, headers=None, params=None):
            return self.api_helper.make_request(endpoint, params=params, headers=headers, method='GET')

    return APIClient(api_helper)

@pytest.fixture(scope="session")
def valid_api_key(config):
    api_key = config.get('authentication', {}).get('api_key')
    if not api_key:
        raise ValueError("Valid API key is not set in the configuration.")
    return api_key

@pytest.fixture(scope="session")
def invalid_api_key():
    return "INVALID_API_KEY"

@pytest.fixture(scope="session")
def valid_location():
    return "San Francisco"

@pytest.fixture(scope="session")
def oauth2_token(config):
    token = config.get('authentication', {}).get('petstore_auth')
    if not token:
        raise ValueError("OAuth2 token is not set in the configuration.")
    return token

@pytest.fixture(scope="session")
def schema_validator():
    return SchemaValidator()

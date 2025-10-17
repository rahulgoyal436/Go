import pytest
import requests
import yaml
import os
from pathlib import Path
from typing import Dict, Any


class APIHelper:
    def __init__(self, base_url: str):
        self.base_url = base_url
    
    def make_request(self, endpoint: str, params=None, headers=None, method='GET') -> requests.Response:
        url = f"{self.base_url}{endpoint.strip()}"
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
            return response
        except requests.RequestException as e:
            raise RuntimeError(f"Request failed: {e}")


class SchemaValidator:
    def validate_schema_order(self, order_data: Dict[str, Any]) -> bool:
        """Validate Order object schema"""
        required_fields = ['id', 'petId', 'quantity', 'shipDate', 'status', 'complete']
        return all(field in order_data for field in required_fields)

    def validate_schema_category(self, category_data: Dict[str, Any]) -> bool:
        """Validate Category object schema"""
        required_fields = ['id', 'name']
        return all(field in category_data for field in required_fields)

    def validate_schema_user(self, user_data: Dict[str, Any]) -> bool:
        """Validate User object schema"""
        required_fields = ['id', 'username', 'firstName', 'lastName', 'email', 'password', 'phone', 'userStatus']
        return all(field in user_data for field in required_fields)

    def validate_schema_tag(self, tag_data: Dict[str, Any]) -> bool:
        """Validate Tag object schema"""
        required_fields = ['id', 'name']
        return all(field in tag_data for field in required_fields)

    def validate_schema_pet(self, pet_data: Dict[str, Any]) -> bool:
        """Validate Pet object schema"""
        required_fields = ['name', 'photoUrls']
        return all(field in pet_data for field in required_fields)

    def validate_schema_api_response(self, api_response_data: Dict[str, Any]) -> bool:
        """Validate ApiResponse object schema"""
        required_fields = ['code', 'type', 'message']
        return all(field in api_response_data for field in required_fields)


@pytest.fixture(scope='session')
def config():
    """Load configuration from YAML file"""
    config_path = Path(__file__).parent / 'config.yml'
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")
    
    with config_path.open('r') as file:
        try:
            raw_config = yaml.safe_load(file)
        except yaml.YAMLError as e:
            raise RuntimeError(f"Failed to parse config file: {e}")
    
    def resolve_env_vars(value):
        if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
            env_var = value[2:-1]
            return os.getenv(env_var, None)
        return value
    
    resolved_config = {k: resolve_env_vars(v) if isinstance(v, str) else v for k, v in raw_config.items()}
    
    return resolved_config


@pytest.fixture(scope='session')
def api_helper(config):
    """Provide an API helper instance"""
    base_url = config['api']['host']
    return APIHelper(base_url)


@pytest.fixture(scope='session')
def api_client(api_helper):
    """Provide an API client with simplified methods"""
    class APIClient:
        def get(self, endpoint, headers=None, params=None):
            return api_helper.make_request(endpoint, method='GET', headers=headers, params=params)
        
    return APIClient()


@pytest.fixture(scope='session')
def valid_api_key(config):
    """Provide a valid API key"""
    return config['authentication']['api_key']


@pytest.fixture(scope='session')
def invalid_api_key():
    """Provide an invalid API key"""
    return "INVALID_API_KEY"


@pytest.fixture(scope='session')
def valid_location():
    """Provide a valid location value"""
    return {"location": "New York"}


@pytest.fixture(scope='session')
def oauth2_token(config):
    """Provide an OAuth2 token"""
    return config['authentication']['petstore_auth']


@pytest.fixture(scope='session')
def schema_validator():
    """Provide the schema validator instance"""
    return SchemaValidator()

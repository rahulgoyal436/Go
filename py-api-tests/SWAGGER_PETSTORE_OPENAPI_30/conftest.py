import os
import yaml
import pytest
import requests
from pathlib import Path
from typing import Dict, Any

# Load configuration from YAML file
@pytest.fixture(scope="session")
def config():
    config_path = Path(__file__).parent / 'config.yml'
    if not config_path.is_file():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    with config_path.open('r') as file:
        raw_config = yaml.safe_load(file)
    
    # Replace ${var} with environment variables
    def resolve_env_vars(value):
        if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
            return os.getenv(value[2:-1], "")
        return value

    resolved_config = {
        key: (resolve_env_vars(value) if isinstance(value, str) else value)
        for key, value in raw_config.items()
    }
    return resolved_config

# Helper class for making API requests
@pytest.fixture(scope="session")
def api_helper(config):
    class APIHelper:
        def __init__(self, base_url):
            self.base_url = base_url.strip()
        
        def make_request(self, endpoint, params=None, headers=None, method='GET'):
            url = f"{self.base_url}/{endpoint.strip()}"
            response = requests.request(method, url, params=params, headers=headers)
            response.raise_for_status()  # Raise exception for bad responses
            return response.json()

    return APIHelper(config['api']['host'])

# Simple API client
@pytest.fixture(scope="session")
def api_client(api_helper):
    class APIClient:
        def get(self, endpoint, headers=None, params=None):
            return api_helper.make_request(endpoint, params=params, headers=headers, method='GET')

    return APIClient()

# Valid API key fixture
@pytest.fixture(scope="session")
def valid_api_key(config):
    return config['authentication']['api_key']

# Invalid API key fixture
@pytest.fixture(scope="session")
def invalid_api_key():
    return "INVALID_API_KEY_123"

# Valid location fixture for testing purposes
@pytest.fixture(scope="session")
def valid_location():
    return "New York"

# OAuth2 token fixture
@pytest.fixture(scope="session")
def oauth2_token(config):
    return config['authentication']['petstore_auth']

# Dynamic schema validation methods
def generate_validation_functions():
    component_schemas = {
        "Order": {
            "properties": {
                "id": {}, "petId": {}, "quantity": {}, "shipDate": {}, 
                "status": {}, "complete": {}
            }
        },
        "Category": {
            "properties": {"id": {}, "name": {}}
        },
        "User": {
            "properties": {
                "id": {}, "username": {}, "firstName": {}, "lastName": {}, 
                "email": {}, "password": {}, "phone": {}, "userStatus": {}
            }
        },
        "Tag": {
            "properties": {"id": {}, "name": {}}
        },
        "Pet": {
            "required": ["name", "photoUrls"],
            "properties": {"id": {}, "name": {}, "category": {}, 
                           "photoUrls": {}, "tags": {}, "status": {}}
        },
        "ApiResponse": {
            "properties": {"code": {}, "type": {}, "message": {}}
        }
    }

    def validate(schema_name, data):
        schema = component_schemas.get(schema_name, {})
        required_fields = schema.get("required", list(schema["properties"].keys()))
        return all(field in data for field in required_fields)

    validation_functions = {}
    for schema_name in component_schemas.keys():
        def func(data, schema_name=schema_name):  # Capture schema_name correctly
            return validate(schema_name, data)
        func.__name__ = f"validate_{schema_name.lower()}_schema"
        func.__doc__ = f'Validate {schema_name} object schema'
        validation_functions[func.__name__] = func

    return validation_functions

# Register dynamically created validation functions as fixtures
for name, func in generate_validation_functions().items():
    globals()[name] = pytest.fixture(scope="session")(func)

__all__ = [
    "config", "api_helper", "api_client", "valid_api_key",
    "invalid_api_key", "valid_location", "oauth2_token"
] + list(generate_validation_functions().keys())

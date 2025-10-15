import pytest
import requests
import yaml
import os
import pathlib
from typing import Dict, Any

# Helper to load configuration from YAML file
def load_config():
    config_path = pathlib.Path(__file__).parent / 'config.yml'
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file {config_path} not found")

    with config_path.open('r') as f:
        config = yaml.safe_load(f)

    def replace_env_variables(value):
        if isinstance(value, str) and value.startswith('${') and value.endswith('}'):
            env_var = value[2:-1]
            return os.getenv(env_var, '')
        return value

    def resolve_nested_env_variables(data):
        if isinstance(data, dict):
            return {key: resolve_nested_env_variables(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [resolve_nested_env_variables(item) for item in data]
        else:
            return replace_env_variables(data)

    return resolve_nested_env_variables(config)

# Helper Class for API Requests
class ApiHelper:
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url.strip()

    def make_request(self, endpoint: str, params=None, headers=None, method='GET'):
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        response = requests.request(method, url, params=params, headers=headers)
        return response

# Pytest Fixtures
@pytest.fixture(scope="session")
def config():
    return load_config()

@pytest.fixture(scope="session")
def api_helper(config):
    base_url = config['api']['host']
    return ApiHelper(base_url)

@pytest.fixture(scope="session")
def api_client(api_helper):
    return api_helper

@pytest.fixture(scope="session")
def valid_api_key(config):
    return config['authentication']['api_key']

@pytest.fixture(scope="session")
def invalid_api_key():
    return "INVALID_API_KEY"

@pytest.fixture(scope="session")
def valid_location():
    return {"lat": 40.7128, "lon": -74.0060}

@pytest.fixture(scope="session")
def oauth2_token(config):
    return config['authentication']['petstore_auth']

# Dynamic Schema Validation Methods
def generate_validation_methods():
    component_schemas = {
        "Order": {
            "type": "object",
            "properties": {
                "id": {"type": "integer", "example": 10},
                "petId": {"type": "integer", "example": 198772},
                "quantity": {"type": "integer", "example": 7},
                "shipDate": {"type": "string"},
                "status": {"type": "string"},
                "complete": {"type": "boolean"}
            }
        },
        "Category": {
            "type": "object",
            "properties": {
                "id": {"type": "integer", "example": 1},
                "name": {"type": "string", "example": "Dogs"}
            }
        },
        "User": {
            "type": "object",
            "properties": {
                "id": {"type": "integer", "example": 10},
                "username": {"type": "string", "example": "theUser"},
                "firstName": {"type": "string", "example": "John"},
                "lastName": {"type": "string", "example": "James"},
                "email": {"type": "string", "example": "john@email.com"},
                "password": {"type": "string", "example": "12345"},
                "phone": {"type": "string", "example": "12345"},
                "userStatus": {"type": "integer", "example": 1}
            }
        },
        "Tag": {
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "name": {"type": "string"}
            }
        },
        "Pet": {
            "required": ["name", "photoUrls"],
            "type": "object",
            "properties": {
                "id": {"type": "integer", "example": 10},
                "name": {"type": "string", "example": "doggie"},
                "photoUrls": {"type": "array"},
                "tags": {"type": "array"},
                "status": {"type": "string"}
            }
        },
        "ApiResponse": {
            "type": "object",
            "properties": {
                "code": {"type": "integer"},
                "type": {"type": "string"},
                "message": {"type": "string"}
            }
        }
    }

    def create_validation_function(schema_name, schema):
        required_fields = schema.get('required', list(schema['properties'].keys()))

        def validation_function(data: Dict[str, Any]) -> bool:
            """Validate {schema_name} object schema"""
            return all(field in data for field in required_fields)

        validation_function.__doc__ = f"Validate {schema_name} object schema"
        validation_function.__name__ = f"validate_{schema_name.lower()}_schema"
        return validation_function

    validation_functions = {}
    for schema_name, schema in component_schemas.items():
        validation_functions[f"validate_{schema_name.lower()}_schema"] = create_validation_function(schema_name, schema)

    return validation_functions

validation_methods = generate_validation_methods()
globals().update(validation_methods)

import pytest
import requests
import os
from pathlib import Path
import yaml
import re


class APIHelper:
    def __init__(self, base_url):
        self.base_url = base_url.rstrip("/")

    def make_request(self, endpoint, params=None, headers=None, method='GET'):
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
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


class APIClient:
    def __init__(self, api_helper):
        self.api_helper = api_helper

    def get(self, endpoint, headers=None, params=None):
        return self.api_helper.make_request(endpoint, params=params, headers=headers, method='GET')


def load_config():
    config_path = Path(__file__).parent / 'config.yml'
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found at {config_path}")
    
    with open(config_path, 'r') as file:
        config_data = yaml.safe_load(file)

    def replace_env_vars(value):
        if isinstance(value, str):
            return re.sub(r'\${(.*?)}', lambda match: os.getenv(match.group(1), ""), value)
        return value

    def recursive_replace(data):
        if isinstance(data, dict):
            return {key: recursive_replace(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [recursive_replace(item) for item in data]
        else:
            return replace_env_vars(data)

    return recursive_replace(config_data)


@pytest.fixture(scope='session')
def config():
    return load_config()


@pytest.fixture(scope='session')
def api_helper(config):
    base_url = config['api']['host']
    return APIHelper(base_url)


@pytest.fixture(scope='session')
def api_client(api_helper):
    return APIClient(api_helper)


@pytest.fixture
def valid_api_key(config):
    return config['authentication']['api_key']


@pytest.fixture
def invalid_api_key():
    return "INVALID_API_KEY"


@pytest.fixture
def valid_location():
    return "test-location"


@pytest.fixture
def oauth2_token(config):
    return config['authentication']['petstore_auth']


@pytest.fixture(scope='session')
def validation_schemas():
    return {
        "Order": {
            "type": "object",
            "properties": {
                "id": {"type": "integer", "format": "int64", "example": 10},
                "petId": {"type": "integer", "format": "int64", "example": 198772},
                "quantity": {"type": "integer", "format": "int32", "example": 7},
                "shipDate": {"type": "string", "format": "date-time"},
                "status": {"type": "string", "description": "Order Status", "example": "approved"},
                "complete": {"type": "boolean"}
            },
            "xml": {"name": "order"}
        },
        "Category": {
            "type": "object",
            "properties": {
                "id": {"type": "integer", "format": "int64", "example": 1},
                "name": {"type": "string", "example": "Dogs"}
            },
            "xml": {"name": "category"}
        },
        "User": {
            "type": "object",
            "properties": {
                "id": {"type": "integer", "format": "int64", "example": 10},
                "username": {"type": "string", "example": "theUser"},
                "firstName": {"type": "string", "example": "John"},
                "lastName": {"type": "string", "example": "James"},
                "email": {"type": "string", "example": "john@email.com"},
                "password": {"type": "string", "example": "12345"},
                "phone": {"type": "string", "example": "12345"},
                "userStatus": {"type": "integer", "description": "User Status", "format": "int32", "example": 1}
            },
            "xml": {"name": "user"}
        },
        "Tag": {
            "type": "object",
            "properties": {
                "id": {"type": "integer", "format": "int64"},
                "name": {"type": "string"}
            },
            "xml": {"name": "tag"}
        },
        "Pet": {
            "required": ["name", "photoUrls"],
            "type": "object",
            "properties": {
                "id": {"type": "integer", "format": "int64", "example": 10},
                "name": {"type": "string", "example": "doggie"},
                "category": {"$ref": "#/components/schemas/Category"},
                "photoUrls": {
                    "type": "array",
                    "xml": {"wrapped": True},
                    "items": {
                        "type": "string",
                        "xml": {"name": "photoUrl"}
                    }
                },
                "tags": {
                    "type": "array",
                    "xml": {"wrapped": True},
                    "items": {"$ref": "#/components/schemas/Tag"}
                },
                "status": {"type": "string", "description": "pet status in the store"}
            },
            "xml": {"name": "pet"}
        },
        "ApiResponse": {
            "type": "object",
            "properties": {
                "code": {"type": "integer", "format": "int32"},
                "type": {"type": "string"},
                "message": {"type": "string"}
            },
            "xml": {"name": "##default"}
        }
    }

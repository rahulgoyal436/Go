import os
import pytest
import requests
import yaml
from pathlib import Path
from typing import Dict, Any

# Load configuration fixture
@pytest.fixture(scope='session')
def config():
    config_path = Path(__file__).parent / "config.yml"
    try:
        with open(config_path, 'r') as file:
            raw_config = yaml.safe_load(file)
        config = {key: os.getenv(value[2:-1]) if isinstance(value, str) and value.startswith('${') else value 
                  for key, value in raw_config.items()}
        return config
    except FileNotFoundError:
        pytest.fail("Configuration file config.yml not found.")
    except Exception as e:
        pytest.fail(f"Error reading config.yml: {e}")

# API Helper class fixture
@pytest.fixture
def api_helper(config):
    class ApiHelper:
        base_url = config['api']['host'].strip()

        def make_request(self, endpoint, params=None, headers=None, method='GET'):
            url = f"{self.base_url}/{endpoint.lstrip('/')}"
            response = requests.request(method, url, params=params, headers=headers)
            return response

    return ApiHelper()

# API Client fixture
@pytest.fixture
def api_client(api_helper):
    class ApiClient:
        def get(self, endpoint, headers=None, params=None):
            return api_helper.make_request(endpoint, params=params, headers=headers, method='GET')

    return ApiClient()

# Fixtures for API authentication and test parameters
@pytest.fixture
def valid_api_key(config):
    return str(config.get('authentication', {}).get('apiKey', ''))

@pytest.fixture
def invalid_api_key():
    return "invalid_api_key_placeholder"

@pytest.fixture
def valid_location():
    return {'latitude': 37.7749, 'longitude': -122.4194}

@pytest.fixture
def oauth2_token(config):
    return str(config.get('authentication', {}).get('oauth2Token', ''))

# SchemaValidator class for schema validation
class SchemaValidator:
    
    def validate_order_schema(self, data: Dict[str, Any]) -> bool:
        required_fields = ['id', 'petId', 'quantity', 'shipDate', 'status', 'complete']
        return all(field in data for field in required_fields)

    def validate_category_schema(self, data: Dict[str, Any]) -> bool:
        required_fields = ['id', 'name']
        return all(field in data for field in required_fields)

    def validate_user_schema(self, data: Dict[str, Any]) -> bool:
        required_fields = ['id', 'username', 'firstName', 'lastName', 'email', 'password', 'phone', 'userStatus']
        return all(field in data for field in required_fields)

    def validate_tag_schema(self, data: Dict[str, Any]) -> bool:
        required_fields = ['id', 'name']
        return all(field in data for field in required_fields)

    def validate_pet_schema(self, data: Dict[str, Any]) -> bool:
        required_fields = ['name', 'photoUrls']
        if not all(field in data for field in required_fields):
            return False
        if 'category' in data:
            required_category_fields = ['id', 'name']
            if not all(field in data['category'] for field in required_category_fields):
                return False
        if 'tags' in data:
            for tag in data['tags']:
                required_tag_fields = ['id', 'name']
                if not all(field in tag for field in required_tag_fields):
                    return False
        return True

    def validate_api_response_schema(self, data: Dict[str, Any]) -> bool:
        required_fields = ['code', 'type', 'message']
        return all(field in data for field in required_fields)

@pytest.fixture
def schema_validator():
    return SchemaValidator()

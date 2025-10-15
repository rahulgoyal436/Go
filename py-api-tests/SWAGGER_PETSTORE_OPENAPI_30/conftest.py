import pytest
import requests
import yaml
import os
from pathlib import Path
from typing import Dict, Any


class APIHelper:
    def __init__(self, base_url: str):
        self.base_url = base_url.strip()

    def make_request(self, endpoint: str, params=None, headers=None, method='GET'):
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        response = requests.request(method, url, params=params, headers=headers)
        return response


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
        required_fields = [
            'id', 'username', 'firstName', 'lastName',
            'email', 'password', 'phone', 'userStatus'
        ]
        return all(field in user_data for field in required_fields)
    
    def validate_tag_schema(self, tag_data: Dict[str, Any]) -> bool:
        """Validate Tag object schema"""
        required_fields = ['id', 'name']
        return all(field in tag_data for field in required_fields)
    
    def validate_pet_schema(self, pet_data: Dict[str, Any]) -> bool:
        """Validate Pet object schema"""
        required_fields = ['name', 'photoUrls']
        has_required = all(field in pet_data for field in required_fields)
        if not has_required:
            return False
        if 'category' in pet_data:
            category_data = pet_data['category']
            category_required = ['id', 'name']
            if not all(field in category_data for field in category_required):
                return False
        if 'tags' in pet_data:
            tags_data = pet_data['tags']
            for tag in tags_data:
                tag_required = ['id', 'name']
                if not all(field in tag for field in tag_required):
                    return False
        return True
    
    def validate_api_response_schema(self, response_data: Dict[str, Any]) -> bool:
        """Validate ApiResponse object schema"""
        required_fields = ['code', 'type', 'message']
        return all(field in response_data for field in required_fields)


@pytest.fixture(scope="session")
def config():
    """Load configuration from YAML file."""
    config_path = Path(__file__).parent / "config.yml"
    try:
        with open(config_path, 'r') as file:
            cfg = yaml.safe_load(file)
            
            # Replace variables like ${VAR} with values from environment
            def resolve_env_variables(value: Any) -> Any:
                if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
                    return os.getenv(value[2:-1])
                return value

            def traverse_and_resolve(obj: Any) -> Any:
                if isinstance(obj, dict):
                    return {k: traverse_and_resolve(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [traverse_and_resolve(item) for item in obj]
                else:
                    return resolve_env_variables(obj)

            resolved_cfg = traverse_and_resolve(cfg)
            return resolved_cfg
    except FileNotFoundError:
        pytest.exit(f"Configuration file not found at {config_path}")
    except yaml.YAMLError as e:
        pytest.exit(f"Error parsing YAML file: {e}")


@pytest.fixture(scope="session")
def api_helper(config):
    """Provide APIHelper instance initialized with base_url."""
    base_url = config.get("api", {}).get("host", "")
    if not base_url:
        pytest.exit("API host configuration is missing in config.yml")
    return APIHelper(base_url=base_url)


@pytest.fixture(scope="session")
def api_client(api_helper):
    """Provide simplified API client."""
    class APIClient:
        def __init__(self, helper: APIHelper):
            self.helper = helper

        def get(self, endpoint, headers=None, params=None):
            """Make GET requests."""
            return self.helper.make_request(endpoint, params=params, headers=headers, method='GET')

    return APIClient(api_helper)


@pytest.fixture(scope="session")
def valid_api_key(config):
    """Provide valid API key."""
    return config.get("authentication", {}).get("valid_api_key", "")


@pytest.fixture(scope="session")
def invalid_api_key():
    """Provide dummy invalid API key."""
    return "invalid_api_key"


@pytest.fixture(scope="session")
def valid_location():
    """Provide test location parameter."""
    return "test-location"


@pytest.fixture(scope="session")
def oauth2_token(config):
    """Provide OAuth2 token extracted from config."""
    return config.get("authentication", {}).get("oauth2_token", "")


@pytest.fixture(scope="session")
def schema_validator():
    """Provide instance of SchemaValidator."""
    return SchemaValidator()

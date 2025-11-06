import os
import pytest
import requests
import yaml
from pathlib import Path

# Fixture to load configuration from config.yml
@pytest.fixture(scope="session")
def config():
    config_path = Path(__file__).parent / "config.yml"
    with open(config_path, "r") as file:
        raw_config = yaml.safe_load(file)
    
    def resolve_env_vars(value):
        if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
            env_var = value[2:-1]
            return os.getenv(env_var, "")
        return value

    def parse_config(data):
        if isinstance(data, dict):
            return {key: parse_config(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [parse_config(item) for item in data]
        else:
            return resolve_env_vars(data)

    return parse_config(raw_config)

# Helper class for making HTTP requests
class ApiHelper:
    def __init__(self, base_url):
        self.base_url = base_url.strip("/")

    def make_request(self, endpoint, params=None, headers=None, method="GET"):
        url = f"{self.base_url}/{endpoint.strip('/')}"
        response = requests.request(method, url, params=params, headers=headers)
        return response

# Fixture to create api_helper instance
@pytest.fixture(scope="session")
def api_helper(config):
    base_url = config["api"]["host"]
    return ApiHelper(base_url)

# Simple API client with predefined methods
class ApiClient:
    def __init__(self, api_helper):
        self.api_helper = api_helper

    def get(self, endpoint, headers=None, params=None):
        return self.api_helper.make_request(endpoint, method="GET", headers=headers, params=params)

# Fixture to create api_client instance
@pytest.fixture(scope="session")
def api_client(api_helper):
    return ApiClient(api_helper)

# Fixture to load a valid API key from config
@pytest.fixture(scope="session")
def valid_api_key(config):
    return config["authentication"]["api_key"]

# Fixture to provide an invalid API key for testing
@pytest.fixture(scope="session")
def invalid_api_key():
    return "invalid_api_key"

# Fixture to provide a valid location parameter for testing
@pytest.fixture(scope="session")
def valid_location():
    return "NYC"

# Fixture to load OAuth2 token from config
@pytest.fixture(scope="session")
def oauth2_token(config):
    return config["authentication"]["petstore_auth"]

# Schema validation class
class SchemaValidator:
    def validate_schema_order(self, order_data):
        required_fields = ['id', 'petId', 'quantity', 'shipDate', 'status', 'complete']
        return all(field in order_data for field in required_fields)

    def validate_schema_category(self, category_data):
        required_fields = ['id', 'name']
        return all(field in category_data for field in required_fields)

    def validate_schema_user(self, user_data):
        required_fields = ['id', 'username', 'firstName', 'lastName', 'email', 'password', 'phone', 'userStatus']
        return all(field in user_data for field in required_fields)

    def validate_schema_tag(self, tag_data):
        required_fields = ['id', 'name']
        return all(field in tag_data for field in required_fields)

    def validate_schema_pet(self, pet_data):
        required_fields = ['name', 'photoUrls']
        # Validate top-level fields first
        if not all(field in pet_data for field in required_fields):
            return False
        # Validate nested fields if present
        if "category" in pet_data and not self.validate_schema_category(pet_data["category"]):
            return False
        if "tags" in pet_data and isinstance(pet_data["tags"], list):
            for tag in pet_data["tags"]:
                if not self.validate_schema_tag(tag):
                    return False
        return True

    def validate_schema_api_response(self, response_data):
        required_fields = ['code', 'type', 'message']
        return all(field in response_data for field in required_fields)

# Fixture to provide the schema validator instance
@pytest.fixture(scope="session")
def schema_validator():
    return SchemaValidator()

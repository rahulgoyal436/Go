import os
import pytest
import requests
import yaml
from pathlib import Path
from string import Template


# Helper function to replace placeholders with environment variables
def replace_placeholders(config):
    for key, value in config.items():
        if isinstance(value, str) and "${" in value:
            config[key] = Template(value).substitute(os.environ)
        elif isinstance(value, dict):
            config[key] = replace_placeholders(value)
    return config


# Fixture to load YAML configuration file
@pytest.fixture(scope="session")
def config():
    config_path = Path(__file__).parent / "config.yml"
    if not config_path.exists():
        pytest.fail(f"Config file not found at {config_path}")
    try:
        with open(config_path, "r") as file:
            config_data = yaml.safe_load(file)
        return replace_placeholders(config_data)
    except Exception as e:
        pytest.fail(f"Failed to load config file: {e}")


# Helper class for making API requests
class APIHelper:
    def __init__(self, base_url):
        self.base_url = base_url.rstrip("/")

    def make_request(self, endpoint, params=None, headers=None, method="GET"):
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        try:
            if method.upper() == "GET":
                response = requests.get(url, params=params, headers=headers)
            elif method.upper() == "POST":
                response = requests.post(url, json=params, headers=headers)
            else:
                pytest.fail(f"Unsupported HTTP method: {method}")
            return response
        except requests.RequestException as e:
            pytest.fail(f"Error while making API request: {e}")


# Fixture for APIHelper instance
@pytest.fixture(scope="session")
def api_helper(config):
    return APIHelper(config["api"]["host"])


# Simple API client with convenience methods
class APIClient:
    def __init__(self, api_helper):
        self.api_helper = api_helper

    def get(self, endpoint, headers=None, params=None):
        return self.api_helper.make_request(endpoint, params=params, headers=headers, method="GET")


# Fixture for APIClient instance
@pytest.fixture(scope="session")
def api_client(api_helper):
    return APIClient(api_helper)


# Fixture to provide valid API key
@pytest.fixture(scope="session")
def valid_api_key(config):
    return config["authentication"]["api_key"]


# Fixture for invalid API key
@pytest.fixture(scope="session")
def invalid_api_key():
    return "invalid_api_key_123"


# Fixture for testing valid location parameter
@pytest.fixture(scope="session")
def valid_location():
    return "New York, NY"


# Fixture for OAuth2 token
@pytest.fixture(scope="session")
def oauth2_token(config):
    return config["authentication"]["petstore_auth"]

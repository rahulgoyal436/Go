import os
import pytest
import requests
import yaml
from pathlib import Path
from string import Template

# Fixture to load configuration from config.yml
@pytest.fixture(scope="session")
def config():
    # Resolve the path to the config file
    config_path = Path(__file__).resolve().parent / "config.yml"
    try:
        # Load the YAML file into a dictionary
        with open(config_path, "r") as file:
            raw_config = yaml.safe_load(file)

        # Replace env vars placeholders in config
        def replace_env_vars(value):
            if isinstance(value, str):
                template = Template(value)
                return template.safe_substitute(os.environ)
            elif isinstance(value, dict):
                return {k: replace_env_vars(v) for k, v in value.items()}
            elif isinstance(value, list):
                return [replace_env_vars(item) for item in value]
            return value

        return replace_env_vars(raw_config)
    except FileNotFoundError:
        pytest.fail(f"Configuration file not found: {config_path}")
    except yaml.YAMLError as e:
        pytest.fail(f"Error parsing YAML file: {e}")

# Helper class to make HTTP requests
class APIHelper:
    def __init__(self, base_url):
        self.base_url = base_url.rstrip("/")

    def make_request(self, endpoint, params=None, headers=None, method="GET"):
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        response = requests.request(method=method, url=url, params=params, headers=headers)
        return response

# Fixture to provide the APIHelper instance
@pytest.fixture(scope="session")
def api_helper(config):
    base_url = config["api"]["host"]
    return APIHelper(base_url)

# API client class with simplified methods
class APIClient:
    def __init__(self, api_helper):
        self.api_helper = api_helper

    def get(self, endpoint, headers=None, params=None):
        return self.api_helper.make_request(endpoint, method="GET", headers=headers, params=params)

# Fixture to provide the APIClient instance
@pytest.fixture(scope="session")
def api_client(api_helper):
    return APIClient(api_helper)

# Fixture to provide a valid API key from config
@pytest.fixture(scope="session")
def valid_api_key(config):
    return config["authentication"].get("api_key")

# Fixture to provide an invalid API key for test purposes
@pytest.fixture(scope="session")
def invalid_api_key():
    return "invalid_api_key_123"

# Fixture to provide a valid location parameter for testing
@pytest.fixture(scope="session")
def valid_location():
    return "New York"

# Fixture to provide an OAuth2 token for authorization
@pytest.fixture(scope="session")
def oauth2_token(config):
    return config["authentication"].get("petstore_auth")

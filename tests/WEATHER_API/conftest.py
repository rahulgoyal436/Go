import os
import pytest
import yaml
import requests
from pathlib import Path
from urllib.parse import urljoin


# Helper to load config file
def load_config():
    config_path = Path(__file__).parent / "config.yml"
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found at: {config_path}")
    
    with open(config_path, "r") as file:
        raw_config = yaml.safe_load(file)
    
    def replace_env_variables(value):
        if isinstance(value, str) and value.startswith("${"):
            env_var = value[2:-1]
            return os.getenv(env_var, value)
        return value
    
    # Recursively replace environment variables in the configuration
    def recursive_resolve(config):
        if isinstance(config, dict):
            return {key: recursive_resolve(value) for key, value in config.items()}
        elif isinstance(config, list):
            return [recursive_resolve(item) for item in config]
        else:
            return replace_env_variables(config)
    
    resolved_config = recursive_resolve(raw_config)
    return resolved_config


# Helper class for making HTTP requests
class APIHelper:
    def __init__(self, base_url):
        self.base_url = base_url.rstrip("/")

    def make_request(self, endpoint, params=None, headers=None, method="GET"):
        url = urljoin(self.base_url, endpoint)
        response = requests.request(method=method.upper(), url=url, params=params, headers=headers)
        return response


# Fixture to load configuration
@pytest.fixture(scope="session")
def config():
    return load_config()


# Fixture to provide an API helper object
@pytest.fixture(scope="session")
def api_helper(config):
    base_url = config["api"]["host"].strip()
    return APIHelper(base_url)


# Fixture for a simple API client
@pytest.fixture(scope="session")
def api_client(api_helper):
    class APIClient:
        def __init__(self, helper):
            self.helper = helper

        def get(self, endpoint, headers=None, params=None):
            return self.helper.make_request(endpoint, headers=headers, params=params, method="GET")

    return APIClient(api_helper)


# Fixture for valid API key
@pytest.fixture(scope="session")
def valid_api_key(config):
    return config["authentication"]["ApiKeyAuth"]


# Fixture for invalid API key
@pytest.fixture(scope="session")
def invalid_api_key():
    return "INVALID_API_KEY_123"


# Fixture for a valid location parameter
@pytest.fixture(scope="session")
def valid_location():
    return {"latitude": 40.7128, "longitude": -74.0060}  # Example: New York City


# Fixture for OAuth2 token
@pytest.fixture(scope="session")
def oauth2_token(config):
    return config.get("authentication", {}).get("OAuth2Token")

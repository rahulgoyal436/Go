import os
import pytest
import requests
import yaml
from pathlib import Path

# Helper function for loading environment variables and replacing placeholders in YAML
def replace_env_vars(config):
    for key, value in config.items():
        if isinstance(value, str) and value.startswith("${"):
            env_var = value.strip("${}")
            config[key] = os.getenv(env_var, None)
        elif isinstance(value, dict):
            config[key] = replace_env_vars(value)
    return config

# Load configuration from config.yml
def load_config():
    try:
        config_path = Path(__file__).parent / "config.yml"
        with open(config_path, "r") as file:
            config = yaml.safe_load(file)
            return replace_env_vars(config)
    except FileNotFoundError:
        raise FileNotFoundError("config.yml file not found in the current directory.")
    except yaml.YAMLError:
        raise ValueError("Error parsing the configuration file.")

@pytest.fixture(scope="session")
def config():
    return load_config()

# Helper class for making HTTP requests
class APIHelper:
    def __init__(self, base_url):
        self.base_url = base_url.strip("/ ")

    def make_request(self, endpoint, params=None, headers=None, method="GET"):
        url = f"{self.base_url}/{endpoint.strip('/ ')}"
        try:
            if method.upper() == "GET":
                response = requests.get(url, params=params, headers=headers)
            elif method.upper() == "POST":
                response = requests.post(url, json=params, headers=headers)
            elif method.upper() == "PUT":
                response = requests.put(url, json=params, headers=headers)
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            return response
        except requests.RequestException as e:
            raise RuntimeError(f"HTTP request failed: {e}")

@pytest.fixture(scope="session")
def api_helper(config):
    base_url = config.get("api", {}).get("host")
    if not base_url:
        raise ValueError("API host is not defined in the configuration.")
    return APIHelper(base_url)

# API Client with convenient methods
class APIClient:
    def __init__(self, api_helper):
        self.api_helper = api_helper

    def get(self, endpoint, headers=None, params=None):
        return self.api_helper.make_request(endpoint, headers=headers, params=params, method="GET")

@pytest.fixture(scope="session")
def api_client(api_helper):
    return APIClient(api_helper)

@pytest.fixture(scope="session")
def valid_api_key(config):
    api_key = config.get("authentication", {}).get("api_key")
    if not api_key:
        raise ValueError("Valid API key is not defined in the configuration.")
    return api_key

@pytest.fixture(scope="session")
def invalid_api_key():
    return "invalid_api_key_123456"

@pytest.fixture(scope="session")
def valid_location():
    return "test_location"

@pytest.fixture(scope="session")
def oauth2_token(config):
    oauth_token = config.get("authentication", {}).get("petstore_auth")
    if not oauth_token:
        raise ValueError("OAuth2 token is not defined in the configuration.")
    return oauth_token

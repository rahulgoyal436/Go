import pytest
import os
import yaml
from pathlib import Path
import requests
from copy import deepcopy


@pytest.fixture(scope="session")
def config():
    """Load configuration from the YAML file"""
    try:
        config_path = Path(__file__).parent / "config.yml"
        with open(config_path, "r") as file:
            raw_config = yaml.safe_load(file)
        # Replace ${var} with environment variable values
        resolved_config = _resolve_env_variables(raw_config)
        return resolved_config
    except FileNotFoundError:
        raise FileNotFoundError("config.yml file not found in the directory.")
    except yaml.YAMLError as e:
        raise ValueError(f"Error parsing YAML configuration file: {e}")


def _resolve_env_variables(config):
    """Replace ${VAR} syntax with values from environment variables"""
    if isinstance(config, dict):
        resolved = {}
        for key, value in config.items():
            resolved[key] = _resolve_env_variables(value)
        return resolved
    elif isinstance(config, list):
        return [_resolve_env_variables(item) for item in config]
    elif isinstance(config, str):
        if config.startswith("${") and config.endswith("}"):
            env_var = config[2:-1]
            return os.getenv(env_var, "")
        return config
    else:
        return config


class ApiHelper:
    """Helper class for making HTTP requests"""
    def __init__(self, base_url):
        self.base_url = base_url.rstrip("/")

    def make_request(self, endpoint, params=None, headers=None, method="GET"):
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        try:
            response = requests.request(method=method, url=url, params=params, headers=headers)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            raise RuntimeError(f"HTTP request failed: {e}")


@pytest.fixture(scope="session")
def api_helper(config):
    """Provide an API helper instance with the base URL from the config"""
    base_url = config["api"]["host"].strip()
    return ApiHelper(base_url)


class ApiClient:
    """Simple API client with convenience methods for specific HTTP verbs"""
    def __init__(self, api_helper):
        self.api_helper = api_helper

    def get(self, endpoint, headers=None, params=None):
        return self.api_helper.make_request(endpoint, params=params, headers=headers, method="GET")


@pytest.fixture(scope="session")
def api_client(api_helper):
    """Provide an API client instance"""
    return ApiClient(api_helper)


@pytest.fixture(scope="session")
def valid_api_key(config):
    """Extract valid API key from the configuration"""
    try:
        return config["authentication"]["ApiKeyAuth"].strip()
    except KeyError:
        raise ValueError("Valid API key not found in the configuration.")


@pytest.fixture(scope="session")
def invalid_api_key():
    """Provide a placeholder invalid API key"""
    return "INVALID_API_KEY"


@pytest.fixture(scope="session")
def valid_location():
    """Provide a valid test location parameter"""
    return {"latitude": 40.7128, "longitude": -74.0060}  # Example: New York City


@pytest.fixture(scope="session")
def oauth2_token(config):
    """Extract OAuth2 token from the configuration"""
    try:
        return config["authentication"].get("OAuth2", None).strip()
    except AttributeError:
        raise ValueError("OAuth2 token is not configured.")

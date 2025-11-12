import pytest
import os
import yaml
import requests
from pathlib import Path

class ApiHelper:
    def __init__(self, base_url):
        self.base_url = base_url.rstrip('/')

    def make_request(self, endpoint, params=None, headers=None, method='GET'):
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        response = requests.request(method=method, url=url, headers=headers, params=params)
        return response

class ApiClient:
    def __init__(self, api_helper):
        self.api_helper = api_helper

    def get(self, endpoint, headers=None, params=None):
        return self.api_helper.make_request(endpoint, params=params, headers=headers, method='GET')

@pytest.fixture(scope="session")
def config():
    config_file = Path(__file__).parent / "config.yml"
    if not config_file.exists():
        raise FileNotFoundError(f"Config file not found at location: {config_file}")

    with open(config_file, "r") as f:
        raw_config = yaml.safe_load(f)

    def resolve_env_var(value):
        if value.startswith("${") and value.endswith("}"):
            env_var = value[2:-1]
            return os.environ.get(env_var, "")
        return value

    def recursively_resolve_config(cfg):
        if isinstance(cfg, dict):
            return {k: recursively_resolve_config(v) for k, v in cfg.items()}
        elif isinstance(cfg, list):
            return [recursively_resolve_config(item) for item in cfg]
        elif isinstance(cfg, str):
            return resolve_env_var(cfg)
        else:
            return cfg

    resolved_config = recursively_resolve_config(raw_config)
    return resolved_config

@pytest.fixture(scope="session")
def api_helper(config):
    base_url = config.get("api", {}).get("host", "").strip()
    if not base_url:
        raise ValueError("Base URL is not configured in the config file.")
    return ApiHelper(base_url)

@pytest.fixture(scope="session")
def api_client(api_helper):
    return ApiClient(api_helper)

@pytest.fixture(scope="session")
def valid_api_key(config):
    api_key = config.get("authentication", {}).get("api_key", "").strip()
    if not api_key:
        raise ValueError("Valid API Key is not configured in the config file.")
    return api_key

@pytest.fixture(scope="session")
def invalid_api_key():
    return "invalid_api_key"

@pytest.fixture(scope="session")
def valid_location():
    return "London"  # Replace this with a valid location for your API tests

@pytest.fixture(scope="session")
def oauth2_token(config):
    token = config.get("authentication", {}).get("petstore_auth", "").strip()
    if not token:
        raise ValueError("OAuth2 Token is not configured in the config file.")
    return token

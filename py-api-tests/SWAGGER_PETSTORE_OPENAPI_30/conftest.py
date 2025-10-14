import pytest
import yaml
import requests
from pathlib import Path
import os

class APIHelper:
    def __init__(self, base_url):
        self.base_url = base_url.rstrip("/")

    def make_request(self, endpoint, params=None, headers=None, method="GET"):
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        methods = {
            "GET": requests.get,
            "POST": requests.post,
            "PUT": requests.put,
            "PATCH": requests.patch,
            "DELETE": requests.delete,
        }
        if method not in methods:
            raise ValueError(f"HTTP method {method} not supported")

        response = methods[method](url, params=params, headers=headers)
        return response


class APIClient:
    def __init__(self, api_helper, valid_api_key=None):
        self.api_helper = api_helper
        self.valid_api_key = valid_api_key

    def get(self, endpoint, headers=None, params=None):
        if headers is None:
            headers = {}
        if self.valid_api_key:
            headers["Authorization"] = f"Bearer {self.valid_api_key}"
        return self.api_helper.make_request(endpoint, params=params, headers=headers, method="GET")


@pytest.fixture(scope="session")
def config():
    config_path = Path(__file__).parent / "config.yml"
    if not config_path.is_file():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    with open(config_path, "r", encoding="utf-8") as file:
        try:
            config_data = yaml.safe_load(file)
        except yaml.YAMLError as e:
            raise ValueError("Error loading configuration file") from e

    return config_data


@pytest.fixture(scope="session")
def api_helper(config):
    base_url = config["api"]["host"].strip()
    return APIHelper(base_url)


@pytest.fixture(scope="session")
def api_client(api_helper, valid_api_key):
    return APIClient(api_helper, valid_api_key)


@pytest.fixture(scope="session")
def valid_api_key(config):
    return config["authentication"]["api_key"]


@pytest.fixture(scope="session")
def invalid_api_key():
    return "invalid-api-key-for-testing"


@pytest.fixture(scope="session")
def valid_location():
    return "test-location"


@pytest.fixture(scope="session")
def oauth2_token(config):
    return config["authentication"]["petstore_auth"]

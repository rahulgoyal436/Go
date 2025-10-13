import pytest
import json
import logging
from jsonschema import Draft7Validator, ValidationError
from typing import Dict, Any


# Configure Logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

# Define schemas for POST request and response validation
POST_REQUEST_SCHEMA = {
    "type": "object",
    "properties": {
        "id": {"type": "integer", "format": "int64"},
        "username": {"type": "string"},
        "firstName": {"type": "string"},
        "lastName": {"type": "string"},
        "email": {"type": "string"},
        "password": {"type": "string"},
        "phone": {"type": "string"},
        "userStatus": {"type": "integer", "format": "int32", "description": "User Status"}
    },
    "required": ["id", "username", "email", "password"],
    "additionalProperties": False
}

POST_RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "id": {"type": "integer", "format": "int64"},
        "username": {"type": "string"},
        "firstName": {"type": "string"},
        "lastName": {"type": "string"},
        "email": {"type": "string"},
        "password": {"type": "string"},
        "phone": {"type": "string"},
        "userStatus": {"type": "integer", "format": "int32", "description": "User Status"}
    },
    "required": ["id", "username", "email"],
    "additionalProperties": False
}

# Pre-compile schemas for better performance
_POST_REQUEST_VALIDATOR = Draft7Validator(POST_REQUEST_SCHEMA)
_POST_RESPONSE_VALIDATOR = Draft7Validator(POST_RESPONSE_SCHEMA)


# Helper function for validation
def validate_payload(payload: Dict[str, Any], validator: Draft7Validator):
    try:
        validator.validate(payload)
    except ValidationError as e:
        logger.error(f"Validation error: {e.message}\nPath: {list(e.path)}")
        pytest.fail(f"Validation failed: {e.message}\nPath: {list(e.path)}")


# Fixtures for test payloads
@pytest.fixture
def valid_post_request_payload():
    return {
        "id": 10,
        "username": "theUser",
        "firstName": "John",
        "lastName": "James",
        "email": "john@email.com",
        "password": "12345",
        "phone": "12345",
        "userStatus": 1
    }


@pytest.fixture
def invalid_post_request_payload():
    return {
        "username": "theUser",
        # Missing required fields: id, email, password
        "firstName": "John"
    }


@pytest.fixture
def valid_post_response_payload():
    return {
        "id": 10,
        "username": "theUser",
        "firstName": "John",
        "lastName": "James",
        "email": "john@email.com",
        "password": "12345",
        "phone": "12345",
        "userStatus": 1
    }


@pytest.fixture
def invalid_post_response_payload():
    return {
        "id": "not-an-integer",  # Incorrect type
        "username": "theUser",
        "email": "john@email.com"
    }


# Test cases for POST method

def test_validate_post_request_schema(valid_post_request_payload):
    """
    Validate POST request payload against schema.

    Tests:
    - Required fields presence
    - Field type validation
    - Nested object structure
    - Additional property restrictions
    """
    validate_payload(valid_post_request_payload, _POST_REQUEST_VALIDATOR)


def test_validate_post_request_schema_invalid_payload(invalid_post_request_payload):
    """
    Test POST request payload validation failure scenarios.
    """
    with pytest.raises(pytest.fail.Exception):
        validate_payload(invalid_post_request_payload, _POST_REQUEST_VALIDATOR)


def test_validate_post_response_schema(valid_post_response_payload):
    """
    Validate POST response payload against schema.

    Tests:
    - Required fields presence
    - Field type validation
    - Additional property restrictions
    """
    validate_payload(valid_post_response_payload, _POST_RESPONSE_VALIDATOR)


def test_validate_post_response_schema_invalid_payload(invalid_post_response_payload):
    """
    Test POST response payload validation failure scenarios.
    """
    with pytest.raises(pytest.fail.Exception):
        validate_payload(invalid_post_response_payload, _POST_RESPONSE_VALIDATOR)


@pytest.mark.parametrize("edge_payload", [
    {"id": -1, "username": "", "email": "invalid-email", "password": ""},
    {"id": 0, "username": "short", "email": "test@example.com", "password": "123"},
    {"id": 9999999999, "username": "validUser", "email": "user@email.com", "password": "Password123!"}
])
def test_post_schema_edge_cases(edge_payload):
    """
    Test POST request payload edge cases.

    Tests:
    - Boundary values for integers
    - Required field edge conditions
    """
    try:
        validate_payload(edge_payload, _POST_REQUEST_VALIDATOR)
    except ValidationError as e:
        logger.error(f"Edge case validation failed: {e.message}")

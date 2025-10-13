import pytest
from jsonschema import Draft7Validator, validate, ValidationError
import logging
from typing import Any, Dict
import json

# Initialize logger
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

# Compiled JSON Schemas
GET_RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "id": {"type": "integer"},
        "username": {"type": "string"},
        "firstName": {"type": "string"},
        "lastName": {"type": "string"},
        "email": {"type": "string"},
        "password": {"type": "string"},
        "phone": {"type": "string"},
        "userStatus": {"type": "integer"},
    },
    "additionalProperties": False,
}

PUT_REQUEST_SCHEMA = {
    "type": "object",
    "properties": {
        "id": {"type": "integer"},
        "username": {"type": "string"},
        "firstName": {"type": "string"},
        "lastName": {"type": "string"},
        "email": {"type": "string"},
        "password": {"type": "string"},
        "phone": {"type": "string"},
        "userStatus": {"type": "integer"},
    },
    "additionalProperties": False,
}

# Cached schema validators for performance
GET_RESPONSE_VALIDATOR = Draft7Validator(GET_RESPONSE_SCHEMA)
PUT_REQUEST_VALIDATOR = Draft7Validator(PUT_REQUEST_SCHEMA)


# Fixtures for payload data
@pytest.fixture
def get_response_payload():
    return {
        "id": 1,
        "username": "john_doe",
        "firstName": "John",
        "lastName": "Doe",
        "email": "john@example.com",
        "password": "strongpassword",
        "phone": "1234567890",
        "userStatus": 1,
    }


@pytest.fixture
def put_request_payload():
    return {
        "id": 1,
        "username": "jane_doe",
        "firstName": "Jane",
        "lastName": "Doe",
        "email": "jane@example.com",
        "password": "otherpassword",
        "phone": "9876543210",
        "userStatus": 2,
    }


# Helper function for validation
def validate_schema(data: Dict[str, Any], validator: Draft7Validator):
    try:
        validator.validate(data)
    except ValidationError as e:
        logger.error(f"Validation failed at {list(e.path)}: {e.message}")
        raise


# GET Tests
def test_validate_get_response_schema(get_response_payload):
    """Validate GET response payload against schema."""
    validate_schema(get_response_payload, GET_RESPONSE_VALIDATOR)


@pytest.mark.parametrize(
    "invalid_payload",
    [
        {},  # Missing all fields
        {"id": "string"},  # Incorrect type
        {"extra_field": "extra_value"},  # Additional property
        {"email": 123},  # Incorrect type
    ],
)
def test_get_response_schema_edge_cases(invalid_payload):
    """Validate GET response payload edge cases."""
    with pytest.raises(ValidationError):
        validate_schema(invalid_payload, GET_RESPONSE_VALIDATOR)


# PUT Tests
def test_validate_put_request_schema(put_request_payload):
    """Validate PUT request payload against schema."""
    validate_schema(put_request_payload, PUT_REQUEST_VALIDATOR)


@pytest.mark.parametrize(
    "invalid_payload",
    [
        {},  # Missing all fields
        {"id": "string"},  # Incorrect type
        {"username": True},  # Incorrect type
        {"email": "invalid email"},  # Format validation (strict email expected)
        {"phone": "short"},  # Test length validation, if defined in real schema
    ],
)
def test_put_request_schema_edge_cases(invalid_payload):
    """Validate PUT request payload edge cases."""
    with pytest.raises(ValidationError):
        validate_schema(invalid_payload, PUT_REQUEST_VALIDATOR)


# DELETE Tests
def test_validate_delete_request_schema():
    """DELETE does not have a schema, validate gracefully."""
    assert True  # No schema or payload to validate


def test_validate_delete_response_schema():
    """DELETE response does not have a schema, validate gracefully."""
    assert True  # No schema or payload to validate


# Utilities for logging detailed error messages
def log_schema_diff(expected: Dict, actual: Dict):
    logger.error(json.dumps({"expected": expected, "actual": actual}, indent=2))

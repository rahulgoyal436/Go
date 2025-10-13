import pytest
import json
import logging
from jsonschema import Draft7Validator, ValidationError
from typing import Dict, Any

# Set up logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

# Schemas from OpenAPI Specification
GET_REQUEST_SCHEMA = {
    "type": "object",
    "properties": {
        "username": {
            "type": "string"
        }
    },
    "required": ["username"]
}

GET_RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "id": {
            "type": "integer",
            "format": "int64"
        },
        "username": {
            "type": "string"
        },
        "firstName": {
            "type": "string"
        },
        "lastName": {
            "type": "string"
        },
        "email": {
            "type": "string",
            "format": "email"
        },
        "password": {
            "type": "string"
        },
        "phone": {
            "type": "string"
        },
        "userStatus": {
            "type": "integer",
            "format": "int32"
        }
    },
    "required": ["id", "username", "email", "userStatus"]
}

PUT_REQUEST_SCHEMA = {
    "type": "object",
    "properties": {
        "id": {
            "type": "integer",
            "format": "int64"
        },
        "username": {
            "type": "string"
        },
        "firstName": {
            "type": "string"
        },
        "lastName": {
            "type": "string"
        },
        "email": {
            "type": "string",
            "format": "email"
        },
        "password": {
            "type": "string"
        },
        "phone": {
            "type": "string"
        },
        "userStatus": {
            "type": "integer",
            "format": "int32"
        }
    },
    "required": ["id", "username", "email", "userStatus"]
}

DELETE_REQUEST_SCHEMA = {
    "type": "object",
    "properties": {
        "username": {
            "type": "string"
        }
    },
    "required": ["username"]
}

DELETE_RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "message": {
            "type": "string"
        }
    }
}

# Helper Functions
def validate_payload(schema: Dict[str, Any], payload: Dict[str, Any]) -> None:
    validator = Draft7Validator(schema)
    try:
        validator.validate(payload)
    except ValidationError as e:
        logger.error(f"Validation error at path {list(e.path)}: {e.message}")
        raise pytest.fail(f"Schema validation failed: {e.message}")

# Fixtures
@pytest.fixture
def get_request_payload():
    return {"username": "user1"}

@pytest.fixture
def get_response_payload():
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
def put_request_payload():
    return {
        "id": 10,
        "username": "updatedUser",
        "firstName": "Doe",
        "lastName": "Smith",
        "email": "doe@email.com",
        "password": "password123",
        "phone": "54321",
        "userStatus": 2
    }

@pytest.fixture
def delete_request_payload():
    return {"username": "user1"}

@pytest.fixture
def delete_response_payload():
    return {"message": "User deleted"}

# Test Cases
def test_validate_get_request_schema(get_request_payload):
    """
    Validate GET request payload against schema.
    """
    validate_payload(GET_REQUEST_SCHEMA, get_request_payload)

def test_validate_get_response_schema(get_response_payload):
    """
    Validate GET response payload against schema.
    """
    validate_payload(GET_RESPONSE_SCHEMA, get_response_payload)

def test_get_schema_edge_cases():
    """
    Validate edge cases for GET schema like missing required fields.
    """
    invalid_payloads = [
        {},  # Missing all required fields
        {"username": 123},  # Invalid type for username
    ]
    for payload in invalid_payloads:
        with pytest.raises(ValidationError):
            validate_payload(GET_REQUEST_SCHEMA, payload)

def test_validate_put_request_schema(put_request_payload):
    """
    Validate PUT request payload against schema.
    """
    validate_payload(PUT_REQUEST_SCHEMA, put_request_payload)

def test_validate_delete_request_schema(delete_request_payload):
    """
    Validate DELETE request payload against schema.
    """
    validate_payload(DELETE_REQUEST_SCHEMA, delete_request_payload)

def test_validate_delete_response_schema(delete_response_payload):
    """
    Validate DELETE response payload against schema.
    """
    validate_payload(DELETE_RESPONSE_SCHEMA, delete_response_payload)

def test_delete_schema_edge_cases():
    """
    Validate edge cases for DELETE schema.
    """
    invalid_payloads = [
        {},  # Missing all required fields
        {"username": 123},  # Invalid type for username
    ]
    for payload in invalid_payloads:
        with pytest.raises(ValidationError):
            validate_payload(DELETE_REQUEST_SCHEMA, payload)

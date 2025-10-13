import pytest
import jsonschema
from jsonschema import Draft7Validator
from typing import Dict, Any, List
import logging

# Setup logging
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Compiled Schemas
POST_REQUEST_SCHEMA = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "id": {"type": "integer", "format": "int64", "example": 10},
            "username": {"type": "string", "example": "theUser"},
            "firstName": {"type": "string", "example": "John"},
            "lastName": {"type": "string", "example": "James"},
            "email": {"type": "string", "example": "john@email.com"},
            "password": {"type": "string", "example": "12345"},
            "phone": {"type": "string", "example": "12345"},
            "userStatus": {"type": "integer", "description": "User Status", "format": "int32", "example": 1},
        },
        "required": ["id", "username", "firstName", "lastName", "email", "password", "phone", "userStatus"],
    },
}

POST_RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "id": {"type": "integer", "format": "int64", "example": 10},
        "username": {"type": "string", "example": "theUser"},
        "firstName": {"type": "string", "example": "John"},
        "lastName": {"type": "string", "example": "James"},
        "email": {"type": "string", "example": "john@email.com"},
        "password": {"type": "string", "example": "12345"},
        "phone": {"type": "string", "example": "12345"},
        "userStatus": {"type": "integer", "description": "User Status", "format": "int32", "example": 1},
    },
    "required": ["id", "username", "firstName", "lastName", "email", "password", "phone", "userStatus"],
}

# Fixtures for test payloads
@pytest.fixture
def valid_post_request_payload() -> List[Dict[str, Any]]:
    return [
        {
            "id": 10,
            "username": "theUser",
            "firstName": "John",
            "lastName": "James",
            "email": "john@email.com",
            "password": "12345",
            "phone": "12345",
            "userStatus": 1,
        }
    ]

@pytest.fixture
def valid_post_response_payload() -> Dict[str, Any]:
    return {
        "id": 10,
        "username": "theUser",
        "firstName": "John",
        "lastName": "James",
        "email": "john@email.com",
        "password": "12345",
        "phone": "12345",
        "userStatus": 1,
    }

@pytest.fixture
def invalid_post_request_payload() -> List[Dict[str, Any]]:
    return [
        {
            "id": "invalid_id",  # Invalid type
            "username": "theUser",
            "email": "invalid-email",  # Invalid format
        }
    ]

@pytest.fixture
def invalid_post_response_payload() -> Dict[str, Any]:
    return {
        "id": "invalid_id",  # Invalid type
        "username": 123,  # Invalid type
    }

# Validator utility
def validate_json_schema(instance: Any, schema: Dict[str, Any]) -> None:
    try:
        Draft7Validator(schema).validate(instance)
    except jsonschema.ValidationError as e:
        logger.error(f"Validation error at {list(e.path)}: {e.message}")
        raise

# Test functions
@pytest.mark.parametrize("payload", [valid_post_request_payload()])
def test_validate_post_request_schema(payload):
    """Validate POST request payload against schema."""
    validate_json_schema(payload, POST_REQUEST_SCHEMA)

@pytest.mark.parametrize("payload", [valid_post_response_payload()])
def test_validate_post_response_schema(payload):
    """Validate POST response payload against schema."""
    validate_json_schema(payload, POST_RESPONSE_SCHEMA)

@pytest.mark.parametrize("payload", [invalid_post_request_payload(), invalid_post_response_payload()])
def test_post_schema_edge_cases(payload):
    """Validate edge cases for POST payload schemas."""
    schema = POST_REQUEST_SCHEMA if isinstance(payload, list) else POST_RESPONSE_SCHEMA
    with pytest.raises(jsonschema.ValidationError):
        validate_json_schema(payload, schema)

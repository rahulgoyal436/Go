import pytest
import json
import logging
from jsonschema import Draft7Validator, ValidationError, validate
from typing import Dict, Any
from functools import lru_cache

# Logger setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Schema definitions for POST method
POST_REQUEST_SCHEMA = {
    "type": "object",
    "properties": {
        "id": {"type": "integer"},
        "username": {"type": "string"},
        "firstName": {"type": "string"},
        "lastName": {"type": "string"},
        "email": {"type": "string", "format": "email"},
        "password": {"type": "string"},
        "phone": {"type": "string"},
        "userStatus": {"type": "integer"},
    },
    "required": ["username", "email", "password"],
    "additionalProperties": False,
}

POST_RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "id": {"type": "integer"},
        "username": {"type": "string"},
        "firstName": {"type": "string"},
        "lastName": {"type": "string"},
        "email": {"type": "string", "format": "email"},
        "password": {"type": "string"},
        "phone": {"type": "string"},
        "userStatus": {"type": "integer"},
    },
    "required": ["id", "username", "email"],
    "additionalProperties": False,
}

# Caching compiled schema for performance
@lru_cache
def get_schema_validator(schema: Dict[str, Any]) -> Draft7Validator:
    return Draft7Validator(schema)

# Fixtures for test payloads
@pytest.fixture
def request_payload() -> Dict[str, Any]:
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "securePassword123!"
    }

@pytest.fixture
def response_payload() -> Dict[str, Any]:
    return {
        "id": 1,
        "username": "testuser",
        "email": "test@example.com",
        "firstName": "Test",
        "lastName": "User",
        "phone": "+123456789",
        "userStatus": 1
    }

@pytest.fixture(scope="module", params=[
    {"username": "abc", "email": "invalid-email", "password": "pass123"},
    {"username": "", "email": "valid@example.com", "password": ""},
    {"username": "testuser", "email": "test@example.com", "password": ""},
    {"email": "missingusername@example.com", "password": "pass123"}
])
def edge_case_request_payload(request: Any) -> Dict[str, Any]:
    return request.param

# Test POST request schema
def test_validate_post_request_schema(request_payload: Dict[str, Any]):
    """Validate POST request payload against schema."""
    schema_validator = get_schema_validator(POST_REQUEST_SCHEMA)
    try:
        schema_validator.validate(request_payload)
    except ValidationError as e:
        logger.error("Validation failed: %s", e.message)
        logger.error("Error path: %s", list(e.absolute_path))
        raise

def test_validate_post_response_schema(response_payload: Dict[str, Any]):
    """Validate POST response payload against schema."""
    schema_validator = get_schema_validator(POST_RESPONSE_SCHEMA)
    try:
        schema_validator.validate(response_payload)
    except ValidationError as e:
        logger.error("Validation failed: %s", e.message)
        logger.error("Error path: %s", list(e.absolute_path))
        raise

@pytest.mark.parametrize("edge_case_request_payload", [
    {"username": "abc", "email": "invalid-email", "password": "pass123"},
    {"username": "", "email": "valid@example.com", "password": ""},
    {"username": "testuser", "email": "test@example.com", "password": ""},
    {"email": "missingusername@example.com", "password": "pass123"}
], indirect=True)
def test_post_schema_edge_cases(edge_case_request_payload: Dict[str, Any]):
    """Test edge cases for POST request schema."""
    schema_validator = get_schema_validator(POST_REQUEST_SCHEMA)
    try:
        schema_validator.validate(edge_case_request_payload)
        logger.info("Edge case request passed: %s", edge_case_request_payload)
    except ValidationError as e:
        logger.error("Validation failed for edge case: %s", edge_case_request_payload)
        logger.error("Failure reason: %s", e.message)
        logger.error("Error path: %s", list(e.absolute_path))

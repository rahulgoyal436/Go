import pytest
from jsonschema import Draft7Validator, ValidationError
import json
import logging
from typing import Any, Dict, List

# Configure logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

# Example OpenAPI schema for POST request and response
POST_REQUEST_SCHEMA = {
    "type": "object",
    "properties": {
        "id": {"type": "integer", "format": "int64"},
        "petId": {"type": "integer", "format": "int64"},
        "quantity": {"type": "integer", "format": "int32"},
        "shipDate": {"type": "string", "format": "date-time"},
        "status": {"type": "string", "description": "Order Status"},
        "complete": {"type": "boolean"}
    },
    "required": ["id", "petId", "quantity", "shipDate", "status", "complete"]
}

POST_RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "id": {"type": "integer", "format": "int64"},
        "petId": {"type": "integer", "format": "int64"},
        "quantity": {"type": "integer", "format": "int32"},
        "shipDate": {"type": "string", "format": "date-time"},
        "status": {"type": "string", "description": "Order Status"},
        "complete": {"type": "boolean"}
    },
    "required": ["id", "petId", "quantity", "shipDate", "status", "complete"]
}

# Precompile schemas for performance
POST_REQUEST_VALIDATOR = Draft7Validator(POST_REQUEST_SCHEMA)
POST_RESPONSE_VALIDATOR = Draft7Validator(POST_RESPONSE_SCHEMA)

# Pytest fixtures
@pytest.fixture
def valid_request_payload():
    return {
        "id": 10,
        "petId": 198772,
        "quantity": 7,
        "shipDate": "2023-10-20T10:00:00Z",
        "status": "approved",
        "complete": True
    }

@pytest.fixture
def valid_response_payload():
    return {
        "id": 10,
        "petId": 198772,
        "quantity": 7,
        "shipDate": "2023-10-20T10:00:00Z",
        "status": "approved",
        "complete": True
    }

@pytest.fixture(params=[
    {},  # Missing required fields
    {"id": "not-an-integer"},  # Invalid type
    {"quantity": -1},  # Fails range validation
])
def invalid_request_payload(request):
    return request.param

@pytest.fixture(params=[
    {},  # Missing required fields
    {"id": "not-an-integer"},  # Invalid type
    {"quantity": -1},  # Fails range validation
])
def invalid_response_payload(request):
    return request.param

# Test functions
def validate_schema(validator: Draft7Validator, payload: Dict[str, Any], schema_type: str) -> None:
    """Helper function to validate schema and log errors."""
    try:
        validator.validate(payload)
    except ValidationError as e:
        logger.error(
            "%s validation error at %s: %s", 
            schema_type, 
            '.'.join(map(str, e.path)),
            e.message
        )
        pytest.fail(f"{schema_type.capitalize()} validation error: {e.message}")

def test_validate_post_request_schema(valid_request_payload):
    """Validate POST request payload against schema."""
    validate_schema(POST_REQUEST_VALIDATOR, valid_request_payload, "request")

def test_validate_post_response_schema(valid_response_payload):
    """Validate POST response payload against schema."""
    validate_schema(POST_RESPONSE_VALIDATOR, valid_response_payload, "response")

@pytest.mark.parametrize("edge_case_payload", [
    {"id": None},  # Null value edge case
    {"id": 1, "petId": 1, "quantity": 0, "shipDate": "", "status": "invalid", "complete": False},
])
def test_post_schema_edge_cases(edge_case_payload):
    """Test edge cases for POST schema."""
    validator = POST_REQUEST_VALIDATOR
    try:
        validator.validate(edge_case_payload)
    except ValidationError as e:
        logger.error(
            "Edge case validation error at %s: %s", 
            '.'.join(map(str, e.path)),
            e.message
        )
        assert e.message, "Unexpected error during edge case validation"

def test_invalid_post_request_schema(invalid_request_payload):
    """Test invalid POST request payload against schema."""
    with pytest.raises(ValidationError):
        POST_REQUEST_VALIDATOR.validate(invalid_request_payload)

def test_invalid_post_response_schema(invalid_response_payload):
    """Test invalid POST response payload against schema."""
    with pytest.raises(ValidationError):
        POST_RESPONSE_VALIDATOR.validate(invalid_response_payload)

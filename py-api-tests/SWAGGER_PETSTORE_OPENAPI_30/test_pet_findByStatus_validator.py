import pytest
import jsonschema
from jsonschema import Draft7Validator
import json
import logging
from typing import Any, Dict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Precompiled JSON schemas for performance
GET_REQUEST_SCHEMA = {
    "type": "object",
    "properties": {
        "status": {
            "type": "string",
            "default": "available"
        }
    },
    "required": [],
}
GET_RESPONSE_SCHEMA = {
    "type": "array",
    "items": {
        "type": "object",
        "required": ["name", "photoUrls"],
        "properties": {
            "id": {"type": "integer", "format": "int64"},
            "name": {"type": "string"},
            "category": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer", "format": "int64"},
                    "name": {"type": "string"}
                }
            },
            "photoUrls": {"type": "array", "items": {"type": "string"}},
            "tags": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer", "format": "int64"},
                        "name": {"type": "string"},
                    }
                }
            },
            "status": {"type": "string"}
        }
    }
}

# Validator initialization
request_validator = Draft7Validator(GET_REQUEST_SCHEMA)
response_validator = Draft7Validator(GET_RESPONSE_SCHEMA)

# Fixtures for test data
@pytest.fixture
def valid_get_request_payload() -> Dict[str, Any]:
    return {"status": "available"}

@pytest.fixture
def valid_get_response_payload() -> Dict[str, Any]:
    return [
        {
            "id": 10,
            "name": "doggie",
            "photoUrls": ["http://example.com/image1.jpg"],
            "category": {"id": 1, "name": "Dogs"},
            "tags": [{"id": 2, "name": "cute"}],
            "status": "available",
        }
    ]

@pytest.fixture
def invalid_get_request_payload() -> Dict[str, Any]:
    return {"status": 123}  # Invalid type

@pytest.fixture
def invalid_get_response_payload() -> Dict[str, Any]:
    return [
        {
            "id": "string instead of integer",
            "name": {"nested": "invalid"},  # Invalid field structure
            "photoUrls": "string instead of array",  # Invalid schema
            "status": 42,
        }
    ]

# Test cases for GET method
@pytest.mark.parametrize("payload, expected_validity", [
    ({"status": "available"}, True),
    ({"status": 123}, False),
    ({}, True),  # Testing optional status field
])
def test_validate_get_request_schema(payload: Dict[str, Any], expected_validity: bool):
    """Validate GET request payload against schema."""
    try:
        request_validator.validate(payload)
        assert expected_validity, f"Expected schema validation to fail for payload: {payload}"
    except jsonschema.ValidationError as e:
        logger.error("Validation Error: %s", e.message)
        assert not expected_validity, f"Unexpected validation success for payload: {payload}"

@pytest.mark.parametrize("payload, expected_validity", [
    ([{
        "id": 10,
        "name": "doggie",
        "photoUrls": ["http://example.com/image1.jpg"],
        "status": "available"
    }], True),
    ([{
        "id": "string instead of integer",
        "name": {"nested": "invalid"},
        "photoUrls": "string instead of array",
        "status": 42
    }], False),
])
def test_validate_get_response_schema(payload: Dict[str, Any], expected_validity: bool):
    """Validate GET response payload against schema."""
    try:
        response_validator.validate(payload)
        assert expected_validity, f"Expected schema validation to fail for payload: {payload}"
    except jsonschema.ValidationError as e:
        logger.error("Validation Error: %s", e.message)
        assert not expected_validity, f"Unexpected validation success for payload: {payload}"

def test_get_schema_edge_cases():
    """Test GET schema edge cases."""
    # Empty payload for response validation
    empty_payload = []
    try:
        response_validator.validate(empty_payload)
        assert True, "Unexpected validation failure for empty payload"
    except jsonschema.ValidationError as e:
        logger.error("Validation Error with empty payload: %s", e.message)
        assert False, "Unexpected validation error for empty payload"

    # Missing required fields
    missing_fields_payload = [{"id": 10}]
    try:
        response_validator.validate(missing_fields_payload)
        assert False, "Expected validation error for missing required fields"
    except jsonschema.ValidationError as e:
        logger.error("Validation Error with missing fields: %s", e.message)
        assert True, "Validation correctly failed for missing fields"

    # Invalid array item type
    invalid_array_item = [{"id": 10, "name": "doggie", "photoUrls": [{}, {}]}]
    try:
        response_validator.validate(invalid_array_item)
        assert False, "Expected validation error for invalid array item type"
    except jsonschema.ValidationError as e:
        logger.error("Validation Error for array items: %s", e.message)
        assert True, "Validation correctly failed for invalid array item type"

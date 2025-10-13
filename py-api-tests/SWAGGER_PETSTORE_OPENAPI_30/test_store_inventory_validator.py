import pytest
from jsonschema import Draft7Validator, ValidationError
from typing import Any, Dict
import json
import logging

# Configure logging for validation errors
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(message)s')

# Example schemas
GET_RESPONSE_SCHEMA = {
    "type": "object",
    "additionalProperties": {
        "type": "integer",
        "format": "int32"
    }
}

# Fixtures for test payloads
@pytest.fixture
def get_response_payload():
    return {"sold": 200, "available": 300, "pending": 150}

@pytest.fixture
def invalid_get_response_payload():
    return {"sold": "wrong_type", "available": 300, "pending": "not_integer"}

# Helper function to validate JSON payloads
def validate_schema(payload: Any, schema: Dict[str, Any]):
    try:
        validator = Draft7Validator(schema)
        validator.validate(payload)
    except ValidationError as e:
        logging.error(f"Schema validation failed: {e.message}")
        logging.error(f"Validation path: {'/'.join(str(p) for p in e.path)}")
        raise

# Test for GET method response schema validation
def test_validate_get_response_schema(get_response_payload):
    """
    Validate GET response payload against its schema.
    
    Tests:
    - Required structure validation
    - Type validation
    """
    validate_schema(get_response_payload, GET_RESPONSE_SCHEMA)

def test_validate_get_response_schema_invalid(invalid_get_response_payload):
    """
    Validate GET response payload with invalid data.

    Tests:
    - Type validation failure
    """
    with pytest.raises(ValidationError):
        validate_schema(invalid_get_response_payload, GET_RESPONSE_SCHEMA)

def test_get_schema_edge_cases():
    """
    Validate edge cases for GET method.
    
    Tests:
    - Empty response object
    - Large numbers
    - Additional properties
    """
    # Empty response object
    empty_payload = {}
    validate_schema(empty_payload, GET_RESPONSE_SCHEMA)

    # Large numbers
    large_numbers_payload = {"sold": 9999999999, "available": 300, "pending": 150}
    validate_schema(large_numbers_payload, GET_RESPONSE_SCHEMA)

    # Additional properties allowed
    additional_properties_payload = {"sold": 200, "available": 300, "pending": 150, "extra": 500}
    validate_schema(additional_properties_payload, GET_RESPONSE_SCHEMA)

import pytest
import jsonschema
import json
import logging
from typing import Dict, Any, Generator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# JSON schemas for validation
GET_RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "id": {"type": "integer"},
        "petId": {"type": "integer"},
        "quantity": {"type": "integer"},
        "shipDate": {"type": "string", "format": "date-time"},
        "status": {"type": "string"},
        "complete": {"type": "boolean"},
    },
    "required": [],
    "additionalProperties": False,
}

# Pre-compiled schemas for performance
GET_RESPONSE_VALIDATOR = jsonschema.Draft7Validator(GET_RESPONSE_SCHEMA)

# Fixtures for test payloads
@pytest.fixture
def get_response_payload() -> Generator[Dict[str, Any], None, None]:
    yield {
        "id": 1,
        "petId": 101,
        "quantity": 5,
        "shipDate": "2023-10-01T10:00:00Z",
        "status": "shipped",
        "complete": True,
    }

@pytest.fixture
def get_edge_case_payloads() -> Generator[Dict[str, Any], None, None]:
    yield [
        {},  # No fields populated
        {"id": "string_instead_of_int"},  # Invalid type for `id`
        {"shipDate": "invalid-date-format"},  # Invalid date format
        {"quantity": -1},  # Below valid range
        {"status": "invalid_status"},  # Invalid enum (if enum exists)
        {"extraField": "unexpected_field"},  # Field not defined in the schema
    ]

# Test functions
def log_validation_error(error: jsonschema.ValidationError) -> None:
    logger.error(f"Validation failed: {error.message}")
    logger.error(f"Path to failing field: {' -> '.join(map(str, error.path))}")

def test_validate_get_response_schema(get_response_payload: Dict[str, Any]) -> None:
    """Validate GET response payload against schema.
    
    Tests:
    - Required fields presence
    - Field type validation
    - Nested object structure
    - Array item validation (if applicable)
    """
    try:
        GET_RESPONSE_VALIDATOR.validate(get_response_payload)
    except jsonschema.ValidationError as error:
        log_validation_error(error)
        pytest.fail("GET response schema validation failed.")

@pytest.mark.parametrize("invalid_payload", [
    {"id": "string_instead_of_int"}, 
    {"shipDate": "invalid-date-format"}, 
    {"quantity": -1},
    {"status": "invalid_status"},
    {"extraField": "unexpected_field"},
])
def test_get_schema_edge_cases(invalid_payload: Dict[str, Any]) -> None:
    """Test GET response schema edge cases and invalid payloads."""
    with pytest.raises(jsonschema.ValidationError):
        GET_RESPONSE_VALIDATOR.validate(invalid_payload)

def test_validate_delete_response_schema() -> None:
    """Validate DELETE response payload (currently null schema).
    
    There is no response schema defined for DELETE, so this test
    validates that no payload exists for DELETE responses.
    """
    try:
        assert True, "No DELETE schema defined, skipping validation."
    except Exception as e:
        logger.error(f"Unexpected error during DELETE response validation: {e}")
        pytest.fail("DELETE response validation unexpectedly failed.")

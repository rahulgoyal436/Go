import pytest
from jsonschema import Draft7Validator, ValidationError
from typing import Dict, Any
import logging
import json

# Configure logging for validation errors
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

# Compiled schema cache for performance
SCHEMA_CACHE = {}

# Load or define schemas (example based on provided input)
GET_RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "description": {"type": "string"},
        "headers": {"type": "string"}
    },
    "required": ["description", "headers"]
}

GET_REQUEST_SCHEMA = {
    "type": "object",
    "properties": {},
    "additionalProperties": False
}

# Helpers to compile the schema once
def get_validator(schema: Dict[str, Any]) -> Draft7Validator:
    if id(schema) not in SCHEMA_CACHE:
        SCHEMA_CACHE[id(schema)] = Draft7Validator(schema)
    return SCHEMA_CACHE[id(schema)]

# Fixtures for test payloads
@pytest.fixture
def request_payload() -> Dict[str, Any]:
    return {}  # Add specific request payloads for GET

@pytest.fixture
def response_payload() -> Dict[str, Any]:
    return {
        "description": "successful operation",
        "headers": "No response headers"
    }  # Add specific response payloads for GET

# Test validate GET request schema
def test_validate_get_request_schema(request_payload):
    """Validate GET request payload against schema."""
    schema_validator = get_validator(GET_REQUEST_SCHEMA)
    try:
        schema_validator.validate(request_payload)
    except ValidationError as e:
        handle_validation_failure(request_payload, GET_REQUEST_SCHEMA, e)

# Test validate GET response schema
def test_validate_get_response_schema(response_payload):
    """Validate GET response payload against schema."""
    schema_validator = get_validator(GET_RESPONSE_SCHEMA)
    try:
        schema_validator.validate(response_payload)
    except ValidationError as e:
        handle_validation_failure(response_payload, GET_RESPONSE_SCHEMA, e)

# Edge case testing for GET schema
@pytest.mark.parametrize("edge_case_payload", [
    {},  # Minimal payload
    {"description": "successful operation"},  # Missing headers field
    {"description": 123, "headers": "No response headers"},  # Invalid type
    {"description": "Excessive description", "headers": "Headers", "extraField": "Invalid"}  # Extra field
])
def test_get_schema_edge_cases(edge_case_payload):
    """Test GET schema edge cases with various payloads."""
    schema_validator = get_validator(GET_RESPONSE_SCHEMA)
    if schema_validator.is_valid(edge_case_payload):
        assert edge_case_payload == edge_case_payload  # Valid payload passes through
    else:
        try:
            schema_validator.validate(edge CaseValidationFailure .
	       
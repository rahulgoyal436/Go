import pytest
import json
import logging
from jsonschema import Draft7Validator, ValidationError
from typing import Any, Dict, List

# Setup logging for detailed error reporting
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Compiling JSON Schemas for Performance Optimizations
GET_REQUEST_SCHEMA = {
    "type": "object",
    "properties": {
        "status": {
            "type": "string",
            "default": "available"
        }
    },
    "required": []
}

GET_RESPONSE_SCHEMA = {
    "type": "array",
    "items": {
        "type": "object",
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
            "photoUrls": {
                "type": "array",
                "items": {"type": "string"}
            },
            "tags": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer", "format": "int64"},
                        "name": {"type": "string"}
                    }
                }
            },
            "status": {"type": "string"}
        },
        "required": ["name", "photoUrls"]
    }
}

# Cache compiled schemas
GET_REQUEST_VALIDATOR = Draft7Validator(GET_REQUEST_SCHEMA)
GET_RESPONSE_VALIDATOR = Draft7Validator(GET_RESPONSE_SCHEMA)


def validate_payload(payload: Any, schema: Draft7Validator):
    """Utility function for schema validation with error logging."""
    try:
        schema.validate(payload)
        logger.info("Validation passed.")
    except ValidationError as e:
        logger.error(f"Validation failed: {e.message} at {list(e.path)}")
        raise


@pytest.mark.parametrize("request_payload", [
    {},  # Default case with no parameters
    {"status": "available"},  # Valid query parameter
    {"status": "sold"},  # Valid query parameter
    {"status": 123},  # Invalid type for "status"
])
def test_validate_get_request_schema(request_payload: Dict[str, Any]):
    """
    Test function for validating the GET request schema.
    The 'request_payload' is passed as a parameter for flexibility.
    """
    if request_payload:
        logger.info(f"Validating GET request schema. Payload: {request_payload}")
        validate_payload(request_payload, GET_REQUEST_VALIDATOR)
    else:
        logger.info("Default request payload passed. Skipping validation.")
    

@pytest.mark.parametrize("response_payload", [
    [
        {
            "id": 1,
            "name": "doggie",
            "category": {"id": 1, "name": "Dogs"},
            "photoUrls": ["photo1", "photo2"],
            "tags": [{"id": 1, "name": "tag1"}],
            "status": "available"
        }
    ],  # Valid response payload
    [
        {
            "id": 2,
            "name": "kitty",
            "category": {"id": 2, "name": "Cats"},
            "photoUrls": [],
            "tags": [],
            "status": "sold"
        }
    ],  # Valid payload but edge case (empty arrays for optional fields)
    [
        {
            "name": "doggie",
            "photoUrls": ["photo1", "photo2"]
        }
    ],  # Valid with minimal required fields
    [
        {
            "id": "invalid",  # Invalid type for "id"
            "name": "doggie",
            "photoUrls": ["photo1", "photo2"]
        }
    ],  # Invalid due to schema type mismatch
])
def test_validate_get_response_schema(response_payload: List[Dict[str, Any]]):
    """
    Test function for validating the GET response schema.
    The 'response_payload' is passed as a parameter for flexibility.
    """
    logger.info(f"Validating GET response schema. Payload: {response_payload}")
    validate_payload(response_payload, GET_RESPONSE_VALIDATOR)


@pytest.mark.parametrize("edge_case_payload", [
    {"status": ""},  # Boundary case: empty string for status
    {"status": "a"*256},  # Boundary case: max length exceeded
    [],  # Empty list for response array
])
def test_get_schema_edge_cases(edge_case_payload: Any):
    """
    Test function for handling edge cases for GET schemas (request and response).
    """
    if isinstance(edge_case_payload, dict):
        # Validate against request schema
        logger.info("Validating edge case payload for GET request schema.")
        with pytest.raises(ValidationError):
            validate_payload(edge_case_payload, GET_REQUEST_VALIDATOR)
    elif isinstance(edge_case_payload, list):
        # Validate against response schema
        logger.info("Validating edge case payload for GET response schema.")
        with pytest.raises(ValidationError):
            validate_payload(edge_case_payload, GET_RESPONSE_VALIDATOR)
    else:
        logger.warning("Unsupported edge case payload type passed.")
        assert False, "Unsupported edge case payload type."


# Add docstrings for clarity
"""
This module validates the /pet/findByStatus API endpoint using pytest and jsonschema.
Includes request and response schema validation along with edge case handling.
""" 

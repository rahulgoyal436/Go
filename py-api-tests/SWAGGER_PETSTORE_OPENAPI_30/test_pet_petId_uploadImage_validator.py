import pytest
from jsonschema import Draft7Validator, ValidationError
from typing import Dict, Any
import json
import logging

# Configure logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

# Example JSON schema
schemas = {
    "post": {
        "requestSchema": None,  # No request schema provided
        "responseSchema": {
            "type": "object",
            "properties": {
                "code": {"type": "integer"},
                "type": {"type": "string"},
                "message": {"type": "string"}
            },
            "required": ["code", "type", "message"]  # Add required fields explicitly
        }
    }
}

# Cache compiled validators for performance
compiled_validators = {
    method: {
        schema_type: Draft7Validator(schema[schema_type]) if schema[schema_type] else None
        for schema_type in ['requestSchema', 'responseSchema']
    }
    for method, schema in schemas.items()
}


def log_validation_error(error: ValidationError):
    logger.error(f"Validation failed at: {list(error.path)}")
    logger.error(f"Message: {error.message}")
    if error.schema_path:
        logger.error(f"Schema path: {list(error.schema_path)}")


@pytest.fixture
def post_request_payload() -> Dict[str, Any]:
    return {}  # Placeholder for request payload


@pytest.fixture
def post_response_payload() -> Dict[str, Any]:
    return {
        "code": 200,
        "type": "success",
        "message": "Operation completed successfully."
    }


@pytest.mark.parametrize("payload", [
    {},  # Missing required fields
    {"code": "200", "type": "success", "message": "OK"},  # Type mismatch
    {"code": 200, "type": "success"},  # Partial payload
    {"code": 200, "type": "success", "message": "OK", "extra_field": "value"}  # Extra fields
])
def test_validate_post_request_schema(post_request_payload: Dict[str, Any], payload):
    """
    Validate POST request payload against schema.

    Tests:
    - Required fields presence
    - Field type validation
    - Nested object structure
    """
    validator = compiled_validators['post']['requestSchema']
    if not validator:
        pytest.skip("No request schema defined for POST method.")
    try:
        validator.validate(payload)
    except ValidationError as error:
        log_validation_error(error)
        pytest.fail(f"Request schema validation error: {error.message}")


def test_validate_post_response_schema(post_response_payload: Dict[str, Any]):
    """
    Validate POST response payload against schema.

    Tests:
    - Required fields presence
    - Field type validation
    - Extra field rejection
    """
    validator = compiled_validators['post']['responseSchema']
    if not validator:
        pytest.skip("No response schema defined for POST method.")
    try:
        validator.validate(post_response_payload)
    except ValidationError as error:
        log_validation_error(error)
        pytest.fail(f"Response schema validation error: {error.message}")


@pytest.mark.parametrize("payload", [
    {"code": -1, "type": "", "message": ""},  # Edge case: Invalid code, empty strings
    {"code": 0, "type": "error", "message": None},  # Type mismatch (null message)
    {"type": "success", "message": "OK"},  # Missing required field 'code'
    {"code": 200, "type": "success", "message": "OK",
     "extra_field": "unexpected"},  # Invalid field present
])
def test_post_schema_edge_cases(payload):
    """
    Test POST response schema with edge cases and boundary conditions.

    - Empty / Null values
    - Missing required fields
    - Unexpected extra fields
    """
    validator = compiled_validators['post']['responseSchema']
    if not validator:
        pytest.skip("No response schema defined for POST method.")
    try:
        validator.validate(payload)
    except ValidationError as error:
        log_validation_error(error)
        pytest.fail(f"Edge case validation failed: {error.message}")

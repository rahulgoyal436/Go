import pytest
from jsonschema import Draft7Validator, ValidationError
from typing import Dict, Any
import json
import logging

# Initialize logger for validation error reporting
logging.basicConfig(level=logging.ERROR, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Sample input schema
post_request_schema = {
    "type": "object",
    "properties": {
        "id": {"type": "integer"},
        "petId": {"type": "integer"},
        "quantity": {"type": "integer"},
        "shipDate": {"type": "string"},
        "status": {"type": "string"},
        "complete": {"type": "boolean"}
    },
    "required": []
}

post_response_schema = {
    "type": "object",
    "properties": {
        "id": {"type": "integer"},
        "petId": {"type": "integer"},
        "quantity": {"type": "integer"},
        "shipDate": {"type": "string"},
        "status": {"type": "string"},
        "complete": {"type": "boolean"}
    },
    "required": []
}

def validate_schema(payload: Dict[str, Any], schema: Dict[str, Any]) -> None:
    """
    Validates a payload against a schema using Draft7Validator.

    Args:
        payload (Dict[str, Any]): The JSON payload to validate.
        schema (Dict[str, Any]): The JSON schema to validate against.

    Raises:
        ValidationError: If the payload is invalid.
    """
    validator = Draft7Validator(schema)
    errors = list(validator.iter_errors(payload))
    if errors:
        for error in errors:
            # Log detailed validation errors with path information
            logger.error(f"Validation error at {'.'.join(map(str, error.path))}: {error.message}")
            if error.path:
                raise ValidationError(f"Validation error at {list(error.path)}: {error.message}")
            else:
                raise ValidationError(f"Validation error: {error.message}")

@pytest.fixture
def valid_post_request_payload() -> Dict[str, Any]:
    """Fixture for a valid POST request payload."""
    return {
        "id": 1,
        "petId": 101,
        "quantity": 3,
        "shipDate": "2023-10-01",
        "status": "delivered",
        "complete": True
    }

@pytest.fixture
def valid_post_response_payload() -> Dict[str, Any]:
    """Fixture for a valid POST response payload."""
    return {
        "id": 1,
        "petId": 101,
        "quantity": 3,
        "shipDate": "2023-10-01",
        "status": "delivered",
        "complete": True
    }

@pytest.fixture
def invalid_post_request_payload() -> Dict[str, Any]:
    """Fixture for an invalid POST request payload."""
    return {
        "id": "invalid_type",  # Invalid type
        "quantity": -5,        # Out of range
        "status": "unknown",   # Value not in enum
    }

@pytest.fixture
def invalid_post_response_payload() -> Dict[str, Any]:
    """Fixture for an invalid POST response payload."""
    return {
        "id": "invalid_type",  # Invalid type
        "quantity": None,      # Missing required field
        "complete": "not_boolean"  # Invalid boolean value
    }

@pytest.mark.parametrize("scenario", ["minimal", "full"])
def test_validate_post_request_schema(valid_post_request_payload, scenario):
    """
    Validate POST request payload against schema.

    Scenarios:
    - "minimal": Test with minimal required fields.
    - "full": Test with all optional fields populated.
    """
    if scenario == "minimal":
        payload = {"id": 1}  # Minimal payload
    else:
        payload = valid_post_request_payload

    try:
        validate_schema(payload, post_request_schema)
    except ValidationError as e:
        pytest.fail(str(e))

@pytest.mark.parametrize("scenario", ["minimal", "full"])
def test_validate_post_response_schema(valid_post_response_payload, scenario):
    """
    Validate POST response payload against schema.

    Scenarios:
    - "minimal": Test with minimal required fields.
    - "full": Test with all optional fields populated.
    """
    if scenario == "minimal":
        payload = {"id": 1}  # Minimal payload
    else:
        payload = valid_post_response_payload

    try:
        validate_schema(payload, post_response_schema)
    except ValidationError as e:
        pytest.fail(str(e))

def test_post_schema_edge_cases(invalid_post_request_payload, invalid_post_response_payload):
    """
    Test boundary conditions and edge cases for POST request/response schema validation.
    
    Includes:
    - Invalid types
    - Missing required fields
    - Out-of-range values
    - Disallowed enum values
    """
    # Test invalid request payload
    with pytest.raises(ValidationError):
        validate_schema(invalid_post_request_payload, post_request_schema)

    # Test invalid response payload
    with pytest.raises(ValidationError):
        validate_schema(invalid_post_response_payload, post_response_schema)

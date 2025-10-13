import pytest
import json
import logging
from jsonschema import Draft7Validator, ValidationError
from typing import Any, Dict

# Configure logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger.addHandler(handler)

# Compiled JSON schemas
GET_REQUEST_SCHEMA = {
    "type": "object",
    "properties": {
        "orderId": {
            "type": "integer",
            "format": "int64"
        }
    },
    "required": ["orderId"]
}

GET_RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "id": {"type": "integer", "format": "int64"},
        "petId": {"type": "integer", "format": "int64"},
        "quantity": {"type": "integer", "format": "int32"},
        "shipDate": {"type": "string", "format": "date-time"},
        "status": {"type": "string"},
        "complete": {"type": "boolean"}
    },
    "required": ["id", "petId", "quantity", "shipDate", "status", "complete"]
}

DELETE_REQUEST_SCHEMA = {
    "type": "object",
    "properties": {
        "orderId": {
            "type": "integer",
            "format": "int64"
        }
    },
    "required": ["orderId"]
}

DELETE_RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "message": {"type": "string"}
    }
}

# Fixtures
@pytest.fixture
def valid_get_request_payload() -> Dict[str, Any]:
    return {"orderId": 1}

@pytest.fixture
def valid_get_response_payload() -> Dict[str, Any]:
    return {
        "id": 10,
        "petId": 198772,
        "quantity": 7,
        "shipDate": "2023-10-05T12:00:00Z",
        "status": "approved",
        "complete": True
    }

@pytest.fixture
def valid_delete_request_payload() -> Dict[str, Any]:
    return {"orderId": 500}

@pytest.fixture
def valid_delete_response_payload() -> Dict[str, Any]:
    return {"message": "Order deleted successfully"}

# Utility function for schema validation
def validate_schema(payload: Dict[str, Any], schema: Dict[str, Any], schema_type: str) -> None:
    validator = Draft7Validator(schema)
    try:
        validator.validate(payload)
    except ValidationError as e:
        error_path = '.'.join(str(step) for step in e.path)
        logger.error(f"Schema validation failed for {schema_type} at {error_path}: {e.message}")
        raise AssertionError(f"Schema validation error: {e.message}")

# Tests for GET method
def test_validate_get_request_schema(valid_get_request_payload):
    """Validate GET request payload against schema."""
    validate_schema(valid_get_request_payload, GET_REQUEST_SCHEMA, 'GET Request')

def test_validate_get_response_schema(valid_get_response_payload):
    """Validate GET response payload against schema."""
    validate_schema(valid_get_response_payload, GET_RESPONSE_SCHEMA, 'GET Response')

@pytest.mark.parametrize("edge_case_payload", [
    ({}),  # Missing required fields
    {"orderId": "invalid"},  # Incorrect type
    {"orderId": -1}  # Invalid range
])
def test_get_schema_edge_cases(edge_case_payload):
    """Test edge cases for GET request schema validation."""
    with pytest.raises(AssertionError):
        validate_schema(edge_case_payload, GET_REQUEST_SCHEMA, 'GET Request')

# Tests for DELETE method
def test_validate_delete_request_schema(valid_delete_request_payload):
    """Validate DELETE request payload against schema."""
    validate_schema(valid_delete_request_payload, DELETE_REQUEST_SCHEMA, 'DELETE Request')

def test_validate_delete_response_schema(valid_delete_response_payload):
    """Validate DELETE response payload against schema."""
    validate_schema(valid_delete_response_payload, DELETE_RESPONSE_SCHEMA, 'DELETE Response')

@pytest.mark.parametrize("edge_case_payload", [
    {},  # Missing required fields
    {"orderId": "string"},  # Incorrect type
    {"orderId": 2000}  # Out-of-range value
])
def test_delete_schema_edge_cases(edge_case_payload):
    """Test edge cases for DELETE request schema validation."""
    with pytest.raises(AssertionError):
        validate_schema(edge_case_payload, DELETE_REQUEST_SCHEMA, 'DELETE Request')

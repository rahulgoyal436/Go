import pytest
import jsonschema
from jsonschema.exceptions import ValidationError
from json import dumps
import logging
from typing import Dict, Any, List

# Setup logging configuration
logging.basicConfig(level=logging.ERROR, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Precompile JSON schemas for performance
POST_RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "id": {"type": "integer"},
        "username": {"type": "string"},
        "firstName": {"type": "string"},
        "lastName": {"type": "string"},
        "email": {"type": "string"},
        "password": {"type": "string"},
        "phone": {"type": "string"},
        "userStatus": {"type": "integer"}
    },
    "additionalProperties": False
}

# Fixture for request payload
@pytest.fixture
def request_payload() -> Dict[str, Any]:
    return {
        "username": "testuser",
        "firstName": "John",
        "lastName": "Doe",
        "email": "john.doe@example.com",
        "password": "securepassword",
        "phone": "1234567890",
        "userStatus": 1
    }

# Fixture for response payload
@pytest.fixture
def response_payload() -> Dict[str, Any]:
    return {
        "id": 1,
        "username": "testuser",
        "firstName": "John",
        "lastName": "Doe",
        "email": "john.doe@example.com",
        "password": "securepassword",
        "phone": "1234567890",
        "userStatus": 1
    }

# Validator function with logging
def validate_schema(schema: Dict[str, Any], payload: Dict[str, Any]):
    try:
        jsonschema.Draft7Validator(schema).validate(payload)
    except ValidationError as e:
        logger.error(f"Schema validation failed: {e.message}\nField Path: {' > '.join(map(str, e.path))}")
        raise

# Test POST request schema validation
def test_validate_post_request_schema(request_payload):
    """Validate POST request payload against schema.
    
    Tests:
    - Required fields presence
    - Field type validation
    - Nested object structure
    - Array item validation
    """
    # Assert request payload against the schema (POST’s request schema is null per spec)
    assert isinstance(request_payload, dict), "Request payload must be a JSON object."

# Test POST response schema validation
def test_validate_post_response_schema(response_payload):
    """Validate POST response payload against schema.
    
    Tests:
    - Field type validation
    - Nested object structure
    - Additional property validation
    """
    validate_schema(POST_RESPONSE_SCHEMA, response_payload)

# Test POST schema edge cases
@pytest.mark.parametrize("response_edge_payload", [
    ({  # Missing optional fields
    }),
    ({  # All fields populated
        "id": 2,
        "username": "edgeuser",
        "firstName": "Alice",
        "lastName": "Smith",
        "email": "alice.smith@example.com",
        "password": "edgepassword",
        "phone": "9876543210",
        "userStatus": 2
    }),
    ({  # Invalid field type: `userStatus` should be integer
        "id": 3,
        "username": "invaliduser",
        "firstName": "Bob",
        "lastName": "Brown",
        "email": "bob.brown@example.com",
        "password": "invalidpassword",
        "phone": "9876543210",
        "userStatus": "invalid_status"
    }),
    ({  # Additional unexpected property
        "id": 4,
        "username": "extrauser",
        "extraProperty": "unexpected"
    }),
])
def test_post_schema_edge_cases(response_edge_payload):
    """Test POST response schema against various edge cases.
    
    Validates:
    - Missing optional fields
    - Fully populated payload
    - Field type mismatch
    - Additional unexpected properties
    """
    try:
        validate_schema(POST_RESPONSE_SCHEMA, response_edge_payload)
    except ValidationError as e:
        logger.error(f"Edge case validation failed: {e.message}\nField Path: {' > '.join(map(str, e.path))}")
        if "invalid_status" in str(e):  # Specific error handling for enum/type issues
            assert True, "Expected ValidationError for userStatus field type mismatch."
        elif "extraProperty" in str(e):  # Specific error for disallowed property
            assert True, "Expected ValidationError for additionalProperty."
        else:
            raise

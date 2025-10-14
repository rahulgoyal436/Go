from jsonschema import validate, ValidationError


# Request schema definition
REQUEST_SCHEMA = {
    "type": "object",
    "properties": {
        "status": {
            "type": "string",
            "default": "available",
        }
    },
    "required": [],
    "additionalProperties": False
}

# Response schema definition
RESPONSE_SCHEMA = {
    "type": "array",
    "items": {
        "type": "object",
        "required": ["name", "photoUrls"],
        "properties": {
            "id": {
                "type": "integer",
                "format": "int64",
            },
            "name": {
                "type": "string",
            },
            "category": {
                "type": "object",
                "properties": {
                    "id": {
                        "type": "integer",
                        "format": "int64",
                    },
                    "name": {
                        "type": "string",
                    }
                },
            },
            "photoUrls": {
                "type": "array",
                "items": {
                    "type": "string",
                }
            },
            "tags": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {
                            "type": "integer",
                            "format": "int64",
                        },
                        "name": {
                            "type": "string",
                        }
                    },
                }
            },
            "status": {
                "type": "string",
            }
        },
    }
}


def validate_request_schema(request_payload: dict) -> None:
    """
    Validates the request payload against the predefined request JSON schema.

    Args:
        request_payload (dict): The request JSON payload to validate.

    Raises:
        AssertionError: Raised if the validation fails with a detailed message.
    """
    try:
        validate(instance=request_payload, schema=REQUEST_SCHEMA)
        print("Request payload validation passed.")
    except ValidationError as e:
        raise AssertionError(f"Request payload validation failed: {str(e)}")


def validate_response_schema(response_payload: dict) -> None:
    """
    Validates the response payload against the predefined response JSON schema.

    Args:
        response_payload (dict): The response JSON payload to validate.

    Raises:
        AssertionError: Raised if the validation fails with a detailed message.
    """
    try:
        validate(instance=response_payload, schema=RESPONSE_SCHEMA)
        print("Response payload validation passed.")
    except ValidationError as e:
        raise AssertionError(f"Response payload validation failed: {str(e)}")

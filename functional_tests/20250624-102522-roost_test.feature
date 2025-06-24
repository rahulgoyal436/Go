Feature: API Testing for User Inputs and System Behavior
  This feature validates the functionality, robustness, and performance of an API responsible for processing and managing user inputs.

  Scenario: Validate that the API accepts valid user input
    Given the API base URL is 'http://localhost:3000'
    When I send a POST request to '/user-input' with the payload:
      """
      {
        "input": "this is a test input"
      }
      """
    Then the response status should be 201
    And the response body should contain:
      """
      {
        "message": "Input accepted successfully"
      }
      """

  Scenario: Validate that the API rejects empty input
    Given the API base URL is 'http://localhost:3000'
    When I send a POST request to '/user-input' with the payload:
      """
      {
        "input": ""
      }
      """
    Then the response status should be 400
    And the response body should contain:
      """
      {
        "error": "Input cannot be empty"
      }
      """

  Scenario: Validate that the API rejects input exceeding the character limit
    Given the API base URL is 'http://localhost:3000'
    When I send a POST request to '/user-input' with a payload of more than 500 characters
    Then the response status should be 413
    And the response body should contain:
      """
      {
        "error": "Input exceeds maximum character limit"
      }
      """

  Scenario: Validate API processing of special characters in input
    Given the API base URL is 'http://localhost:3000'
    When I send a POST request to '/user-input' with the payload:
      """
      {
        "input": "!@#$%^&*"
      }
      """
    Then the response status should be 201
    And the response body should contain:
      """
      {
        "message": "Input accepted successfully"
      }
      """

  Scenario: Validate consistent processing of mixed character input
    Given the API base URL is 'http://localhost:3000'
    When I send a POST request to '/user-input' with the payload:
      """
      {
        "input": "Test123"
      }
      """
    Then the response status should be 201
    And the response body should contain:
      """
      {
        "message": "Input accepted successfully"
      }
      """

  Scenario: Verify response when system notifies user of successful input submission
    Given the API base URL is 'http://localhost:3000'
    When I send a POST request to '/user-input' with the payload:
      """
      {
        "input": "this is a test input"
      }
      """
    Then the response status should be 201
    And the response body should contain:
      """
      {
        "message": "Input submitted successfully"
      }
      """

  Scenario: Validate data persistence after user input submission
    Given the API base URL is 'http://localhost:3000'
    When I send a POST request to '/user-input' with the payload:
      """
      {
        "input": "this is a test input"
      }
      """
    And I send a subsequent GET request to '/user-input'
    Then the response status should be 200
    And the response body should contain:
      """
      {
        "inputs": ["this is a test input"]
      }
      """

  Scenario: Validate duplicate submissions are disallowed
    Given the API base URL is 'http://localhost:3000'
    When I send a POST request to '/user-input' with the payload:
      """
      {
        "input": "duplicate input"
      }
      """
    And I send a second POST request to '/user-input' with the payload:
      """
      {
        "input": "duplicate input"
      }
      """
    Then the response status should be 409
    And the response body should contain:
      """
      {
        "error": "Duplicate input is not allowed"
      }
      """

  Scenario: Validate the system handles high input load efficiently
    Given the API base URL is 'http://localhost:3000'
    When I send 50 POST requests to '/user-input' in under a minute with varying payloads
    Then all responses should have a status of 201
    And there should be no server crashes or timeouts

  Scenario: Validate system response time under normal conditions
    Given the API base URL is 'http://localhost:3000'
    When I send a POST request to '/user-input' with the payload:
      """
      {
        "input": "this is a test input"
      }
      """
    Then the response time should be less than 2 seconds
    And the response status should be 201

  Scenario: Validate API protection against XSS
    Given the API base URL is 'http://localhost:3000'
    When I send a POST request to '/user-input' with the payload:
      """
      {
        "input": "<script>alert('XSS')</script>"
      }
      """
    Then the response status should be 400
    And the response body should contain:
      """
      {
        "error": "Invalid input detected"
      }
      """

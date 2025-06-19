Feature: API Key Update and Validation Scenarios

# Functional Test Scenarios

Scenario: Update the OpenAI API Key with correct credentials
  Given the API base URL 'http://localhost:3000'
  And the OpenAI API endpoint '/update-key'
  And the payload contains a valid API key "{valid_api_key}"
  When I send a POST request to the endpoint with the valid payload
  Then the response status should be 200
  And the response body should confirm 'API key updated successfully'
  And the key update behavior should remain consistent across retries

Scenario: Update an invalid OpenAI API Key
  Given the API base URL 'http://localhost:3000'
  And the OpenAI API endpoint '/update-key'
  And the payload contains an invalid API key "{invalid_api_key}"
  When I send a POST request to the endpoint with the invalid payload
  Then the response status should be 400
  And the response body should contain an error message 'Invalid or expired key'
  And edge-case syntax like empty strings or malformed keys should also cause errors

Scenario: Update OpenAI API Key and invoke dependent function
  Given the API base URL 'http://localhost:3000'
  And the payload contains a valid API key "{valid_api_key}"
  When I send a POST request to '/update-key'
  And I invoke the dependent function "openAi.models.list()"
  Then the response status should be 200
  And the function should execute successfully using the updated key

Scenario: Update OpenAI API Key while testing retry mechanism
  Given the API base URL 'http://localhost:3000'
  And the first attempt fails due to an invalid API key "{invalid_api_key}"
  And after updating with a valid API key "{valid_api_key}"
  When I send a POST request with the updated key in retries
  Then the retry mechanism should use the updated key
  And no stale or undefined values should be utilized

Scenario: Update an invalid key other than OpenAI (e.g., GitHub API)
  Given the API base URL 'http://localhost:3000'
  And the GitHub API endpoint '/update-key'
  And the payload contains invalid credentials "{invalid_github_key}"
  When I send a POST request to the endpoint with invalid GitHub payload
  Then the response should accurately isolate errors to OpenAI keys only
  And ensure validation mechanisms are distinct for other API keys

Scenario: Add validation for empty or undefined OpenAI key
  Given the API base URL 'http://localhost:3000'
  And the OpenAI API endpoint '/update-key'
  And the payload contains an empty value "" or undefined key
  When I send a POST request to the endpoint
  Then the response status should be 400
  And the response body should display 'Invalid OpenAI Key'

Scenario: Remove redundant function calls
  Given the API base URL 'http://localhost:3000'
  And the logic "openAi.models.list()" is removed
  When I execute key update and other dependent functionalities
  Then all functions should operate successfully
  And no errors should occur due to redundant call elimination

# Non-Functional Test Scenarios

Scenario: Performance Impact for Large Number of Retries
  Given the API base URL 'http://localhost:3000'
  And correct credentials are used for OpenAI key updates
  When I simulate concurrent retries under high load
  Then the key update duration should remain within acceptable limits
  And the application should scale efficiently without performance bottlenecks

Scenario: Output Masking for Security
  Given the application logs and error console output
  When an invalid API key "{invalid_api_key}" is sent
  Then the error logs should mask sensitive token details
  And ensure security by obfuscating API key information

Scenario: Usability - Error Message Clarity
  Given an invalid or expired OpenAI key "{invalid_api_key}"
  When I send a POST request to '/update-key'
  Then the response status should be 400
  And the app should display actionable error messages 'Invalid OpenAI Key – Please confirm its validity'

Scenario: Compatibility Across Environments
  Given the API key update functionality
  When I test the feature in development, staging, and production environments
  Then the behavior should remain consistent across them
  And the update mechanism should not experience environment-specific conflicts

Scenario: Scalability for Key Updates Across Other APIs
  Given OpenAI and GitHub API keys need updates simultaneously
  When I attempt concurrent updates for multiple API keys
  Then the application should segregate API key mechanisms effectively
  And ensure scalable behavior during simultaneous updates

Scenario: Security Test Against Injection Vulnerabilities
  Given the OpenAI API endpoint '/update-key'
  And the payload contains a malicious key "{malicious_payload}"
  When I send a POST request to the endpoint
  Then the application should reject the payload and prevent injection
  And log the error securely without compromising the system

Scenario: Stability Across High Stress or Fault Scenarios
  Given multiple users attempt to update API keys concurrently
  When the application is run under simulated high-load conditions
  Then the system should handle stress gracefully
  And ensure key updates are validated and processed reliably without crashing

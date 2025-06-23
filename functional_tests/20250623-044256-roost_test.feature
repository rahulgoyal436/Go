Feature: Testing OpenAI API Key Update Functionality in CLI

  Scenario: Successful API Key Update
    Given the CLI is running with the command for API key update
    When I provide a valid OpenAI API key "sk-VALIDTOKEN12345"
    Then the response message should be "API key updated successfully."
    And the CLI should use the updated key for all subsequent operations
    And no retries should be triggered after the update.

  Scenario: Invalid API Key Update Attempt
    Given the CLI is running with the command for API key update
    When I provide an invalid OpenAI API key "sk-INVALIDTOKEN12345"
    Then the response message should be "Invalid API key. Please try again with a valid key."
    And the CLI should prohibit operations that require OpenAI functionality
    And no changes should be made to the stored API key.

  Scenario: Existing Key Validation After Update
    Given the CLI is running with an existing key "sk-OLDTOKEN12345"
    When I update the API key to "sk-NEWTOKEN12345"
    Then all subsequent OpenAI operations should use "sk-NEWTOKEN12345"
    And the old key "sk-OLDTOKEN12345" should not be used during any operation.

  Scenario: Handling Undefined or Stale Tokens
    Given the CLI is running with the command for API key update
    When I provide an empty value as the API key
    Then the response message should be "API key cannot be empty."
    And the CLI should prevent operations requiring OpenAI functionality.

  Scenario: Token Validation Failure on Retry
    Given the CLI is running and the API key is updated to "sk-FAIL1212"
    When the token validation triggers during retries
    Then the system should perform validation explicitly using "sk-FAIL1212"
    And an appropriate error message should be displayed for validation failure.

  Scenario: Error Message Localization Support 
    Given the CLI language is set to French
    When I provide an invalid OpenAI API key
    Then the response message should be "Clé API invalide. Veuillez réessayer avec une clé valide."
    And similar behavior should be verified for other supported languages.

  Scenario: Conflicting Tokens Across Multiple Threads
    Given Thread 1 is using the API key "sk-ABC12345678"
    And Thread 2 updates the API key to "sk-XYZ98765432"
    When both threads perform OpenAI-related operations
    Then Thread 1 should continue using the old key until operation completion
    And Thread 2's update should globally propagate after operation isolation.

  Scenario: Non-Affected API Keys Validation
    Given the CLI supports API keys for multiple services
    When I attempt to use a GitHub API key "ghp-GITHUBKEY12345" for OpenAI updates
    Then the operation should fail with a message "Invalid key for OpenAI API."
    And the update functionality for unrelated service keys should remain unaffected.

  Scenario: Performance During High-Frequency Key Updates
    Given the CLI is running and automated updates are executed
    When I perform 100 API key updates per minute (valid and invalid)
    Then the CLI should remain responsive without crashes or slowdowns
    And no memory leaks or errors should occur during processing.

  Scenario: Resilience Against Invalid Inputs
    Given the CLI is running with the command for API key update
    When I provide invalid tokens such as "stringonly", "123456", or "!@#$%^&*()"
    Then the system should return valid error messages without crashes
    And invalid tokens should always fail validation checks.

  Scenario: Scalability with Large Tokens
    Given the CLI is running with a character limit for tokens
    When I provide a token longer than 500 characters
    Then the response message should be "Token length exceeds allowed limit."
    And tokens exceeding the limit should not be stored or processed.

  Scenario: CLI Usability in Low-Bandwidth Environments
    Given the CLI is operating in a low-bandwidth environment of 512 Kbps
    When I attempt to update the API token
    Then the CLI should not hang and should return a progress or error message efficiently.

  Scenario: Security Validation for Masking Tokens in Logs
    Given the CLI logs API key operations (valid and invalid)
    When an error or log entry references an API key
    Then the tokens in the logs should be masked as "sk-*****"
    And no raw tokens should be visible in debug or standard output logs.

  Scenario: Power Interruption During Token Update
    Given the CLI is updating the API key
    When the system is abruptly shut down during the update
    Then the system should retain the previous valid token after recovery
    And no incomplete or corrupted tokens should be stored.

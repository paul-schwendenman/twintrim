Feature: Program completes with no action
  Scenario: Program completes no action without other flags
    Given we have "twintrim" installed
    Given we have two matching files "foo.txt" and "foo (1).txt"
    When we run "twintrim" with args: "-n"
    Then "foo (1).txt" still exists
    And "foo.txt" still exists

  Scenario: Program completes no action with full flag
    Given we have "twintrim" installed
    Given we have two matching files "foo.txt" and "foo (1).txt"
    When we run "twintrim" with args: "--no-action"
    Then "foo (1).txt" still exists
    And "foo.txt" still exists

  Scenario: No action with custom pattern flag
    Given we have "twintrim" installed
    And we have two matching files "file__1.txt" and "file.txt"
    When we run "twintrim" with args: "-n -p '(.+?)(?:__\d)*\..*'"
    Then "file.txt" still exists
    And "file__1.txt" still exists

  Scenario: No action with checksum only mode
    Given we have "twintrim" installed
    And we have two matching files "foo.txt" and "foobar.txt"
    When we run "twintrim" with args: "-n -c"
    Then "foo.txt" still exists
    And "foobar.txt" still exists

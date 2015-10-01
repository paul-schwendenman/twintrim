Feature: Program runs recusively with recursive flag
  Scenario: Program works recursively with -r flag
    Given we have "twintrim" installed
    And we have a subdirectory "recur"
    And we have two matching files "recur/foo.txt" and "recur/foo (1).txt"
    And we have two matching files "bar.txt" and "bar (2).txt"
    When we run "twintrim" with args: "-r"
    Then "recur/foo.txt" still exists
    But "recur/foo (1).txt" is removed
    And "bar.txt" still exists
    But "bar (2).txt" is removed

  Scenario: Program works recursively with full word arg
    Given we have "twintrim" installed
    And we have a subdirectory "recur"
    And we have two matching files "recur/foo.txt" and "recur/foo (1).txt"
    And we have two matching files "bar.txt" and "bar (2).txt"
    When we run "twintrim" with args: "--recursive"
    Then "recur/foo.txt" still exists
    But "recur/foo (1).txt" is removed
    And "bar.txt" still exists
    But "bar (2).txt" is removed

  Scenario: Program works recursively with full word arg
    Given we have "twintrim" installed
    And we have a subdirectory "recur"
    And we have two matching files "recur/foo.txt" and "recur/foo (1).txt"
    And we have two matching files "bar.txt" and "bar (2).txt"
    When we run "twintrim" with no args
    Then "bar.txt" still exists
    And "recur/foo.txt" still exists
    But "recur/foo (1).txt" still exists
    But "bar (2).txt" is removed

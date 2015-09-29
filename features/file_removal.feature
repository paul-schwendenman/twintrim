Feature: remove failed # features/file_removal.feature:1
  Scenario: Remove one of two files
    Given we have "twintrim" installed
    Given we have two files "foo.txt" and "foo (2).txt"
    When we run "twintrim" with no args
    Then "foo (2).txt" is removed
    And "foo.txt" still exists

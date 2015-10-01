Feature: program removes hard links rather than skipping file
  Scenario: Remove one of two hard linked files
    Given we have "twintrim" installed
    Given we have two linked files "foo.txt" and "foo (2).txt"
    When we run "twintrim" with args: "--remove-links"
    Then "foo (2).txt" is removed
    And "foo.txt" still exists

  Scenario: Skip deleting two hard linked files
    Given we have "twintrim" installed
    Given we have two linked files "foo.txt" and "foo (2).txt"
    When we run "twintrim" with no args
    Then "foo (2).txt" is link of "foo.txt"

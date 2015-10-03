Feature: Remove duplicate files
  Scenario: Remove one of two files
    Given we have "twintrim" installed
    Given we have two matching files "foo.txt" and "foo (2).txt"
    When we run "twintrim" with no args
    Then "foo (2).txt" is removed
    And "foo.txt" still exists

  Scenario: Program doesn't delete files with different checksums
    Given we have "twintrim" installed
    And we have two different files "foo.txt" and "foo (1).txt"
    When we run "twintrim" with no args
    Then "foo.txt" still exists
    And "foo (1).txt" still exists

  Scenario: Program deletes matching sums with different names in checksum mode
    Given we have "twintrim" installed
    And we have two matching files "foo.txt" and "foobar.txt"
    When we run "twintrim" with args: "-c"
    Then "foo.txt" still exists
    But "foobar" is removed

  Scenario: Multiple files exist some matching some different
    Given we have "twintrim" installed
    And we have two matching files "foo.txt" and "foo (3).txt"
    And we have two different files "foo (1).txt" and "foo (2).txt"
    When we run "twintrim" with no args
    Then "foo.txt" still exists
    And "foo (1).txt" is removed
    And "foo (2).txt" still exists
    But "foo (3).txt" is removed

  Scenario: Base file doesn't exist leaving files with same length names
    Given we have "twintrim" installed
    And we have two matching files "foo (4).txt" and "foo (3).txt"
    And we have two different files "foo (1).txt" and "foo (2).txt"
    When we run "twintrim" with no args
    Then "foo (1).txt" still exists
    And "foo (2).txt" still exists
    But "foo (3).txt" is removed
    And "foo (4).txt" is removed

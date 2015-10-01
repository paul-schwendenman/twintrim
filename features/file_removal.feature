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
    And "foo.txt" still exists

  Scenario: Program deletes matching sums with different names in checksum mode
    Given we have "twintrim" installed
    And we have two matching files "foo.txt" and "foobar.txt"
    When we run "twintrim" with args: "-c"
    Then "foo.txt" still exists
    But "foobar" is removed

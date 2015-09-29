Feature: remove failed # features/file_removal.feature:1
  Scenario: Remove one of two files
    Given we have "twintrim" installed
    Given we have two files "foo.txt" and "foo (2).txt"
    When we run "twintrim" with no args
    Then "foo (2).txt" is removed
    And "foo.txt" still exists

    Scenario: Program completes no action with -n flag
      Given we have "twintrim" installed
      Given we have two files "foo.txt" and "foo (1).txt"
      When we run "twintrim" with args: "-n"
      Then "foo (1).txt" still exists
      And "foo.txt" still exists

    Scenario: Program doesn't delete files different checksums
      Given we have "twintrim" installed
      And we have two different files "foo.txt" and "foo (1).txt"
      When we run "twintrim" with no args
      Then "foo.txt" still exists
      And "foo.txt" still exists

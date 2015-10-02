Feature: User starts program interactively
  Scenario: Program listens to use input for deleting file
    Given we have "twintrim" installed
    Given we have two matching files "foo.txt" and "foo (1).txt"
    When we run "twintrim" with interactive mode
    Then "foo (1).txt" still exists
    But "foo.txt" is removed

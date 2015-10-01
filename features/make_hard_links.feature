Feature: program makes hard links rather than deleting file
  Scenario: Remove one of two files
    Given we have "twintrim" installed
    Given we have two matching files "foo.txt" and "foo (2).txt"
    When we run "twintrim" with args: "--make-link"
    Then "foo (2).txt" is link of "foo.txt"

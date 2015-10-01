Feature: User can select different hashing functions
  Scenario: Remove one of two files
    Given we have "twintrim" installed
    And we have two matching files "foo.txt" and "foo (2).txt"
    When we run "twintrim" with args: "--hash-function md5"
    Then "foo.txt" still exists
    But "foo (2).txt" is removed

  Scenario: Remove one of two files
    Given we have "twintrim" installed
    And we have two matching files "foo.txt" and "foo (2).txt"
    When we run "twintrim" with args: "--hash-function sha1"
    Then "foo.txt" still exists
    But "foo (2).txt" is removed

  Scenario: Remove one of two files
    Given we have "twintrim" installed
    And we have two matching files "foo.txt" and "foo (2).txt"
    When we run "twintrim" with args: "--hash-function sha256"
    Then "foo.txt" still exists
    But "foo (2).txt" is removed

    Scenario: Remove one of two files
      Given we have "twintrim" installed
      And we have two matching files "foo.txt" and "foo (2).txt"
      When we run "twintrim" with args: "--hash-function sha512"
      Then "foo.txt" still exists
      But "foo (2).txt" is removed

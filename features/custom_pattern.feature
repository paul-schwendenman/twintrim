Feature: Custom pattern matching
  Scenario: Files have __1 appended to them
    Given we have "twintrim" installed
    And we have two matching files "file__1.txt" and "file.txt"
    When we run "twintrim" with args: "-p '(.+?)(?:__\d)*\..*'"
    Then "file.txt" still exists
    But "file__1.txt" is removed

  Scenario: Files have different extensions
    Given we have "twintrim" installed
    And we have two matching files "file.txt~" and "file.txt"
    When we run "twintrim" with args: "-p '(^.+?)(?: \(\d\))*\..+'"
    Then "file.txt" still exists
    But "file.txt~" is removed

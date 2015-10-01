Feature: Program creates a log file
  Scenario: Program completes no action without other flags
    Given we have "twintrim" installed
    Given we have two matching files "foo.txt" and "foo (1).txt"
    When we run "twintrim" with logging: "--log-file logfile.log" and args: "-n"
    Then the logfile exists

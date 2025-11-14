*** Settings ***
Library  LibUsingLoggingApi.py

*** Test Cases ***
Log Levels
    Set log level  TRACE
    Log with all levels
    [Teardown]  Set log level  INFO

Invalid level
    [Documentation]    FAIL ValueError: Invalid log level 'INVALID'.
    Write    This fails    INVALID

FAIL is not valid log level
    [Documentation]    FAIL ValueError: Invalid log level 'FAIL'.
    Write    This fails too    FAIL

Timestamps are accurate
    Log messages different time

Log HTML
    Set log level  DEBUG
    Log HTML
    [Teardown]  Set log level  INFO

Write messages to log and console
    Write messages to log and console

Log Non-Strings
    Log Non Strings

Log Callable
    Log Callable

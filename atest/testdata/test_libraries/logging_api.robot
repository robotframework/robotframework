*** Settings ***
Library  LibUsingLoggingApi.py

*** Test Cases ***
Log Levels
    Set log level  TRACE
    Log with all levels
    [Teardown]  Set log level  INFO

Invalid level
    [Documentation]    FAIL Invalid log level 'INVALID'.
    Write    This fails    INVALID

FAIL is not valid log level
    [Documentation]    FAIL Invalid log level 'FAIL'.
    Write    This fails too    FAIL

Timestamps are accurate
    Log messages different time

Log HTML
    Set log level  DEBUG
    Log HTML
    [Teardown]  Set log level  INFO

Write messages to console
    Write messages to console

Log Non-Strings
    Log Non Strings

Log Callable
    Log Callable

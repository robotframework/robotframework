*** Settings ***
Library  LibUsingLoggingApi.py

*** Test Cases ***

Log Levels
    [Documentation]  FAIL Invalid log level 'INVALID'
    Set log level  TRACE
    Log with all levels
    [Teardown]  Set log level  INFO

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

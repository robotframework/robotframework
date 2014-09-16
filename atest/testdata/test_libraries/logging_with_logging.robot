*** Settings ***
Documentation   Tests for logging using Python's `logging` module.
Library         LibUsingPyLogging.py
Test Teardown   Set Log Level  debug


*** Test Cases ***

All logging is disabled
    Log with default levels
    Log invalid message

Log with default levels
    Log with default levels

Log with custom levels
    [Setup]  Set log level  trace
    Log with custom levels

Messages below threshold level are ignored fully
    [Setup]  Set log level  warn
    Log invalid message

Error in creating message is logged
    Log invalid message

Log using custom logger
    Log using custom logger

Log using non-propagating logger
    Log using non propagating logger

Timestamps are accurate
    Log messages different time

Logging when timeout is in use
    [Timeout]  5 seconds
    Log something

*** Settings ***
Documentation     Tests for logging using stdout/stderr
Suite Setup       Set Log Level    DEBUG
Library           ExampleLibrary
Library           PrintLib.py
Library           String

*** Test Cases ***
Logging Using Stdout And Stderr
    Print    Hello from Python Library!
    Print    Hello to stderr from Python Library!    stderr
    Print to stdout and stderr    Hello!!

Logging With Levels
    [Setup]    Set Log Level    TRACE
    Print with all levels
    [Teardown]    Set Log Level    DEBUG

Message before first level is considered INFO
    Print    Hello\n*INFO* world!
    Print    Hi\nthere\n*DEBUG*again!

Level must be all caps and start a row
    Print    *DeBUG* is not debug
    Print    This is not an *ERROR*

Logging Non-ASCII As Unicode
    Print    Hyvää päivää stdout!
    Print    Hyvää päivää stderr!    stderr

Logging Non-ASCII As Bytes
    ${encoding} =    Evaluate    robot.utils.encoding.OUTPUT_ENCODING    robot
    ${bytes} =    Encode String To Bytes    Hyvää päivää!    ${encoding}
    Print    ${bytes}
    Print    ${bytes}    stderr

Logging Mixed Non-ASCII Unicode And Bytes
    ${encoding} =    Evaluate    robot.utils.encoding.OUTPUT_ENCODING    robot
    ${bytes} =    Encode String To Bytes    Hyvä byte!    ${encoding}
    Print Many    ${bytes}    Hyvä Unicode!

Logging HTML
    Print One HTML Line
    Print Many HTML Lines
    Print HTML To Stderr

FAIL is not valid log level
    Print    *FAIL* is not failure

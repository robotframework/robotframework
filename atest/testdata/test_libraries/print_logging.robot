*** Settings ***
Documentation     Tests for logging using stdout/stderr
Suite Setup       Set Log Level    DEBUG
Library           ExampleLibrary
Library           PrintLib.py
Library           String

*** Variables ***
${CONSOLE_ENCODING}         ASCII    # Should be overridden from CLI

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
    ${bytes} =    Encode String To Bytes    Hyvää päivää!    ${CONSOLE ENCODING}
    Print    ${bytes}
    Print    ${bytes}    stderr

Logging Mixed Non-ASCII Unicode And Bytes
    ${bytes} =    Encode String To Bytes    Hyvä byte!    ${CONSOLE ENCODING}
    Print Many    ${bytes}    Hyvä Unicode!

Logging HTML
    Print One HTML Line
    Print Many HTML Lines
    Print HTML To Stderr

Logging CONSOLE
    Print Console
    Print Console

FAIL is not valid log level
    Print    *FAIL* is not failure

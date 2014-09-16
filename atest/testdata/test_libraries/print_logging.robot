*** Settings ***
Documentation     Tests for logging using stdout/stderr
Library           ExampleLibrary
Library           HtmlPrintLib.py
Library           String

*** Test Cases ***
Logging Using Stdout And Stderr
    Print    Hello from Python Library!
    Print    Hello to stderr from Python Library!    stderr
    Print to stdout and stderr    Hello!!

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

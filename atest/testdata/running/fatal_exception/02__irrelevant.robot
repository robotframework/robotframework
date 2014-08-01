*** Settings ***
Library      NonExisting
Resource     NotEither.txt
Variables    NotHere.py

*** Test Cases ***
Test That Should Not Be Run 2.1
    [Documentation]  FAIL  Test execution stopped due to a fatal error.
    No operation

Test That Should Not Be Run 2.2
    [Documentation]  FAIL  Test execution stopped due to a fatal error.
    No operation

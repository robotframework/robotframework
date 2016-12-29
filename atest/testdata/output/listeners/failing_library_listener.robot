*** Settings ***
Library         LibraryWithFailingListener.py

*** Test Cases ***
Pass
    Log    Hello, world!

Fail
    [Documentation]    FAIL Expected failure
    Fail    Expected failure

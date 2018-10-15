*** Settings ***
Library         listenerlibrary3.py
Suite Setup     Foo

*** Test Cases ***
Pass
    Log     Passing
Fail
    Fail    Failing

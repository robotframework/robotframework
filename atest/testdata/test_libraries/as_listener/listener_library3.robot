*** Settings ***
Library   listenerlibrary3.py
Suite setup     Foo

*** Test Cases ***
Pass
    Log     Passing
Fail
    Fail    Failing

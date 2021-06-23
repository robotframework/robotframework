*** Settings ***
Library          WrappedFunctions.py
Library          WrappedMethods.py

*** Test Cases ***
Wrapped functions
    Wrapped function
    Wrapped function with arguments    arg
    Wrapped function with arguments    arg1    arg2

Wrapped function with wrong number of arguments
    [Documentation]    FAIL
    ...    Keyword 'WrappedFunctions.Wrapped Function With Arguments' expected 1 to 2 arguments, got 0.
    Wrapped function with arguments

Wrapped methods
    Wrapped method
    Wrapped method with arguments    arg
    Wrapped method with arguments    arg1    arg2

Wrapped method with wrong number of arguments
    [Documentation]    FAIL
    ...    Keyword 'WrappedMethods.Wrapped Method With Arguments' expected 1 to 2 arguments, got 0.
    Wrapped method with arguments

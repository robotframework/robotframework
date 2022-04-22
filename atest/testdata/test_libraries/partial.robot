*** Settings ***
Library    PartialFunction.py
Library    PartialMethod.py

*** Test Cases ***
Partial function
    Partial function    value

Partial function with named arguments
    Partial function    value=value

Partial function with argument conversion
    Partial function    VALUE    lower=yes

Partial function with invalid argument count
    [Documentation]    FAIL    Keyword 'PartialFunction.Partial Function' expected 1 non-named argument, got 3.
    Partial function    too    many    args

Partial method
    Partial method    value

Partial method with named arguments
    Partial method    value=value

Partial method with argument conversion
    Partial method    VALUE    lower=yes

Partial method with invalid argument count
    [Documentation]    FAIL    Keyword 'PartialMethod.Partial Method' expected 1 non-named argument, got 0.
    Partial method

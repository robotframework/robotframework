*** Settings ***
Library    Library.py

*** Test Cases ***
Normal and kwargs
    [Documentation]    FAIL Keyword 'Library.Normal And Kwargs' expected 1 non-named argument, got 0.
    Normal and kwargs    arg
    Normal and kwargs    arg    a=1    b=2
    Normal and kwargs    a=1

Varargs and kwargs
    Varargs and kwargs
    Varargs and kwargs    a
    Varargs and kwargs    a    b    c
    Varargs and kwargs    a=1
    Varargs and kwargs    a=1    b=2    c=3
    Varargs and kwargs    a    b    c=3    d=4

Kwargs
    Kwargs
    Kwargs    a=1
    Kwargs    a=1    b=2    c=3
    Kwargs    @{EMPTY}

Invalid kwargs
    [Documentation]    FAIL Keyword 'Library.Varargs And Kwargs' got positional argument after named arguments.
    Varargs and kwargs    a=1    @{EMPTY}    invalid

*** Settings ***
Library         dynamic_libraries/InvalidArgSpecs.py

*** Test Cases ***
Argspec consists of something else than strings
    [Documentation]    FAIL No keyword with name 'Argspec With Other Than Strings' found.
    Argspec With Other Than Strings

Argspec has named arguments before positional
    [Documentation]    FAIL No keyword with name 'Named Args Before Positional' found.
    Named Args Before Positional

Argspec has multiple varargs
    [Documentation]    FAIL No keyword with name 'Multiple Varargs' found.
    Multiple Varargs

Argspec has kwargs before positional arguments
    [Documentation]    FAIL No keyword with name 'Kwargs Before Positional Args' found.
    Kwargs Before Positional Args

Argspec has kwargs before named arguments
    [Documentation]    FAIL No keyword with name 'Kwargs Before Named Args' found.
    Kwargs Before Named Args

Argspec has kwargs before varargs
    [Documentation]    FAIL No keyword with name 'Kwargs Before Varargs' found.
    Kwargs Before Varargs

Keywords with valid arg spec can be used
    ${ret} =    Valid argspec    Hello!
    Should be equal    ${ret}    HELLO!

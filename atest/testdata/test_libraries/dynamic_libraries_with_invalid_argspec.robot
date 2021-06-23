*** Settings ***
Test Template    Keyword should not exist
Library          dynamic_libraries/InvalidArgSpecs.py

*** Test Cases ***
Argspec consists of something else than strings
    Other Than Strings

Argspec has named arguments before positional
    Named Args Before Positional

Argspec has multiple varargs
    Multiple Varargs

Argspec has kwargs before positional arguments
    Kwargs Before Positional Args

Argspec has kwargs before named arguments
    Kwargs Before Named Args

Argspec has kwargs before varargs
    Kwargs Before Varargs

Empty tuple in argspec
    Empty tuple

Too long tuple in argspec
    Too long tuple

Too long tuple in argspec with *varargs and **kwags
    Too long tuple with *varargs
    Too long tuple with **kwargs

Tuple with non-string first value
    Tuple with non-string first value

Keywords with valid arg spec can be used
    [Template]    NONE
    ${ret} =    Valid argspec    Hello!
    Should be equal    ${ret}    HELLO!
    ${ret} =    Valid argspec with tuple    Hello!
    Should be equal    ${ret}    HELLO!
    ${ret} =    Valid argspec with tuple    Hello    world!
    Should be equal    ${ret}    HELLO WORLD!

*** Keywords ***
Keyword Should Not Exist
    [Arguments]    ${name}
    Run Keyword And Expect Error
    ...    No keyword with name '${name}' found.
    ...    Keyword Should Exist    ${name}

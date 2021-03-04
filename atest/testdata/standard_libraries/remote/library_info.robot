*** Settings ***
Library           Remote    http://127.0.0.1:${PORT}
Suite Setup       Set Log Level    DEBUG

*** Variables ***
${PORT}           8270

*** Test Cases ***
Load large library
    ${ret} =    Keyword 0
    Should be equal    ${ret}    0
    ${ret} =    Keyword 9999
    Should be equal    ${ret}    9999

Arguments
    [Documentation]    FAIL Keyword 'Remote.Keyword 0' expected 0 to 1 arguments, got 2.
    Some Keyword    a
    Some Keyword    a    b
    Some Keyword    a    b    c    d    e
    Keyword 0
    Keyword 0    1
    Keyword 0    1    2

Types
    ${ret} =    Some keyword    true
    Should be equal    ${ret}    yes
    ${ret} =    Some keyword    false
    Should be equal    ${ret}    no
    ${ret} =    Keyword 42    -42
    Should be equal    ${ret}    ${-42}

__intro__ is not exposed
    [Documentation]    FAIL No keyword with name '__intro__' found.
    __intro__

__init__ is not exposed
    [Documentation]    FAIL No keyword with name '__init__' found.
    __init__

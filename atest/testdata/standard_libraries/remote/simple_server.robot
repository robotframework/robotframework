*** Settings ***
Documentation     Server has only get_kw_names and run_kw methods and returns minimal result dictionary.
Library           Remote    127.0.0.1:${PORT}
Library           Conflict.py
Suite Setup       Set Log Level    DEBUG

*** Variables ***
${PORT}           8270

*** Test Cases ***
Passing
    Passing
    ${ret} =    Passing    I    can    has    argz?
    Should Be Equal    ${ret}    ${EMPTY}

Failing
    [Documentation]    FAIL Teh error messaz
    Failing    Teh    error    messaz
    Fail    This should not be executed

Failing with traceback
    [Documentation]    FAIL RemoteError
    Traceback    Teh    trazeback
    Fail    This should not be executed

Returning
    ${ret} =    Returning
    Should Be Equal    ${ret}    ${EMPTY}
    ${ret} =    Returning    I    can    has    argz?
    Should Be Equal    ${ret}    I can has argz?

Logging
    ${ret} =    Logging    I can has logz?    *DEBUG* Yezz!!
    Should Be Equal    ${ret}    ${EMPTY}

Extra stuff in result dictionary is ignored
    Extra stuff in result dictionary

Keyword name conflict with custom library
    [Documentation]    FAIL
    ...    Multiple keywords with name 'Conflict' found. \
    ...    Give the full name of the keyword you want to use:
    ...    ${SPACE*4}Conflict.Conflict
    ...    ${SPACE*4}Remote.Conflict
    Conflict

Keyword name conflict with standard library
    Should Be True    False

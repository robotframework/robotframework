*** Settings ***
Test Template     Do uppercase
Library           String

*** Test Cases ***
Convert To Uppercases
    [Template]    Do uppercase
    abcd    ABCD
    1234    1234
    a1b2C3d4e    A1B2C3D4E
    ${EMPTY}    ${EMPTY}
    ööääåå    ÖÖÄÄÅÅ

Convert To Lowercases
    [Template]    Do lowercase
    ABCD    abcd
    1234    1234
    A1B2c3D4E    a1b2c3d4e
    ${EMPTY}    ${EMPTY}
    ÖÖÄÄÅÅ    ööääåå

Convert To Titlecases
    [Template]    Do titlecases
    abcd    Abcd
    jUnit    JUnit
    aBBbcd    ABBbcd
    1234    1234
    a1b2 C3d4e    A1b2 C3d4e
    a1b2 c3d4e    A1b2 C3d4e
    ${EMPTY}    ${EMPTY}

*** Keywords ***
Do uppercase
    [Arguments]    ${arg1}    ${arg2}
    ${result} =    Convert To Uppercase    ${arg1}
    Should be Equal    ${result}    ${arg2}

Do lowercase
    [Arguments]    ${arg1}    ${arg2}
    ${result} =    Convert To Lowercase    ${arg1}
    Should be Equal    ${result}    ${arg2}

Do titlecases
    [Arguments]    ${arg1}    ${arg2}
    ${result} =    Convert To Titlecase    ${arg1}
    Should be Equal    ${result}    ${arg2}

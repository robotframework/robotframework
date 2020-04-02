*** Settings ***
Documentation                 S1
Documentation                 S2
Metadata          Foo         M1
Metadata          Foo         M2
Suite Setup       Log Many    S1
Suite Setup       Comment     S2
Suite Teardown    Comment     S1
Suite Teardown    Log Many    S2
Test Setup        Log Many    T1
Test Setup        Comment     T2
Test Teardown
Test Teardown     Comment     T1
Test Teardown     Log Many    T2
Test Template     Log Many
Test Template     Ignored
Force Tags
Force Tags        F1
Force Tags        F2
Default Tags      D1
Default Tags      D2
Default Tags      D3
Test Timeout      1 s
Test Timeout      0.001 s

*** Test Cases ***
Use Defaults
    Sleep    0.1s

Test Settings
    [Documentation]    T1
    [Documentation]    FAIL 2 s
    [Tags]
    [Tags]    T1
    [Tags]    T2
    [Setup]    Log Many    Own
    [Setup]    stuff    here
    [Teardown]
    [Teardown]    Log Many    And
    [Teardown]    also    here
    [Template]    Log
    [Template]    ignored
    [Timeout]    2 s
    [Timeout]    2 ms
    No Operation

Keyword Settings
    [Template]    NONE
    ${ret} =    Keyword Settings    1   2   3
    Should Be Equal    ${ret}    R0

*** Keywords ***
Keyword Settings
    [Arguments]    ${a1}    ${a2}    ${a3}
    [Arguments]    ${arg}
    [Documentation]
    [Documentation]    K1
    [Documentation]    K2
    [Tags]    K1
    [Tags]    K2
    [Timeout]
    [Timeout]    1s
    [Timeout]    2s
    No Operation
    [Return]    R0
    [Return]    R1
    [Return]    R2
    [Return]    R3

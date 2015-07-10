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
Test Template     Sle
Test Template     ep
Force Tags
Force Tags        F1
Force Tags        F2
Default Tags      D1
Default Tags      D2
Default Tags      D3
Test Timeout      1 ms
Test Timeout      2 s

*** Test Cases ***
Use Defaults
    [Documentation]    FAIL 2 s
    1 s

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
    [Template]    S
    [Template]    leep
    [Timeout]    2 ms
    [Timeout]    2 s
    1 s

Keyword Settings
    [Template]    NONE
    [Timeout]    NONE
    ${ret} =    Keyword Settings    arg
    Should Be Equal    ${ret}    R3

*** Keywords ***
Keyword Settings
    [Arguments]
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
    [Return]
    [Return]    R1
    [Return]    R2
    [Return]    R3

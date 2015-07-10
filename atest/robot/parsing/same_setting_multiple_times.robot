*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    parsing/same_setting_multiple_times.robot
Force Tags       regression    pybot    jybot
Resource         atest_resource.robot

*** Test Cases ***
Suite Documentation
    Should Be Equal    ${SUITE.doc}    S1 S2
    Setting multiple times deprecated    0    Documentation

Suite Metadata
    Should Be Equal    ${SUITE.metadata['Foo']}    M2

Suite Setup
    Keyword data should be     ${SUITE.setup}    BuiltIn.Log Many    args=S1, Comment, S2
    Setting multiple times deprecated    1    Suite Setup

Suite Teardown
    Keyword data should be     ${SUITE.teardown}    BuiltIn.Comment    args=S1, Log Many, S2
    Setting multiple times deprecated    2    Suite Teardown

Force and Default Tags
    Check Test Tags    Use Defaults    F1    F2    D1    D2    D3
    Setting multiple times deprecated    6    Force Tags
    Setting multiple times deprecated    7    Default Tags
    Setting multiple times deprecated    8    Default Tags

Test Setup
    ${tc} =    Check Test Case    Use Defaults
    Keyword data should be     ${tc.setup}    BuiltIn.Log Many    args=T1, Comment, T2
    Setting multiple times deprecated    3    Test Setup

Test Teardown
    ${tc} =    Check Test Case    Use Defaults
    Keyword data should be     ${tc.teardown}    BuiltIn.Comment    args=T1, Log Many, T2
    Setting multiple times deprecated    4    Test Teardown

Test Template
    ${tc} =    Check Test Case    Use Defaults
    Keyword data should be     ${tc.kws[0]}    BuiltIn.Sleep    args=1 s
    Setting multiple times deprecated    5    Test Template

Test Timeout
    ${tc} =    Check Test Case    Use Defaults
    Should Be Equal    ${tc.timeout}    1 millisecond
    Setting multiple times deprecated    9    Test Timeout

Test [Documentation]
    ${tc} =    Check Test Case    Test Settings
    Should Be Equal    ${tc.doc}    T1 FAIL 2 s
    Setting multiple times deprecated in test case table    10    [Documentation]

Test [Tags]
    Check Test Tags    Test Settings    F1    F2    T1    T2
    Setting multiple times deprecated in test case table    11    [Tags]

Test [Setup]
    ${tc} =    Check Test Case    Test Settings
    Keyword data should be     ${tc.setup}    BuiltIn.Log Many    args=Own, stuff, here
    Setting multiple times deprecated in test case table    12    [Setup]

Test [Teardown]
    ${tc} =    Check Test Case    Test Settings
    Keyword data should be     ${tc.teardown}    BuiltIn.Log Many    args=And, also, here
    Setting multiple times deprecated in test case table    13    [Teardown]

Test [Template]
    ${tc} =    Check Test Case    Test Settings
    Keyword data should be     ${tc.kws[0]}    BuiltIn.Sleep   args=1 s
    Setting multiple times deprecated in test case table    14    [Template]

Test [Timeout]
    ${tc} =    Check Test Case    Test Settings
    Should Be Equal    ${tc.timeout}    2 milliseconds
    Setting multiple times deprecated in test case table    15    [Timeout]

Keyword [Arguments]
    ${tc} =    Check Test Case    Keyword Settings
    Keyword data should be    ${tc.kws[0]}    Keyword Settings    assign=\${ret}    args=arg
    Setting multiple times deprecated in keyword table    16    [Arguments]    continuation=no

Keyword [Documentation]
    ${tc} =    Check Test Case    Keyword Settings
    Should Be Equal    ${tc.kws[0].doc}    K1 K2
    Setting multiple times deprecated in keyword table    17    [Documentation]

Keyword [Tags]
    ${tc} =    Check Test Case    Keyword Settings
    Should Be True    list($tc.kws[0].tags) == ['K1', 'K2']
    Setting multiple times deprecated in keyword table    18    [Tags]

Keyword [Timeout]
    ${tc} =    Check Test Case    Keyword Settings
    Should Be Equal    ${tc.kws[0].timeout}    1 second
    Setting multiple times deprecated in keyword table    19    [Timeout]

Keyword [Return]
    Check Test Case    Keyword Settings
    Setting multiple times deprecated in keyword table    20    [Return]    continuation=no
    Setting multiple times deprecated in keyword table    21    [Return]    continuation=no

*** Keywords ***
Setting multiple times deprecated
    [Arguments]    ${index}    ${setting}    ${continuation}=yes    @{extra}
    ${path} =    Normalize Path    ${DATADIR}/parsing/same_setting_multiple_times.robot
    @{parts} =    Create List
    ...    Error in file '${path}':
    ...    @{extra}
    ...    Using ${setting} setting multiple times is deprecated.
    Run Keyword If    "${continuation}" == "yes"
    ...    Append To List    ${parts}    Use '...' syntax for line continuation instead.
    ${msg} =    Catenate    @{parts}
    Check Log Message      @{ERRORS}[${index}]    ${msg}   WARN

Setting multiple times deprecated in test case table
    [Arguments]    ${index}    ${setting}    ${continuation}=yes
    Setting multiple times deprecated    ${index}    ${setting}    ${continuation}
    ...    Invalid syntax in test case 'Test Settings':

Setting multiple times deprecated in keyword table
    [Arguments]    ${index}    ${setting}    ${continuation}=yes
    Setting multiple times deprecated    ${index}    ${setting}    ${continuation}
    ...    Invalid syntax in keyword 'Keyword Settings':

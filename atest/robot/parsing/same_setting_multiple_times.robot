*** Settings ***
Suite Setup      Run Tests    -L TRACE    parsing/same_setting_multiple_times.robot
Resource         atest_resource.robot

*** Test Cases ***
Suite Documentation
    Should Be Equal    ${SUITE.doc}    ${EMPTY}
    Setting multiple times    0    Documentation

Suite Metadata
    Should Be Equal    ${SUITE.metadata['Foo']}    M2

Suite Setup
    Should Be Equal    ${SUITE.setup}    ${NONE}
    Setting multiple times    1    Suite Setup

Suite Teardown
    Should Be Equal    ${SUITE.teardown}    ${NONE}
    Setting multiple times    2    Suite Teardown

Force and Default Tags
    Check Test Tags    Use Defaults
    Setting multiple times    7     Force Tags
    Setting multiple times    8     Force Tags
    Setting multiple times    9     Default Tags
    Setting multiple times    10    Default Tags

Test Setup
    ${tc} =    Check Test Case    Use Defaults
    Should Be Equal    ${tc.setup}    ${NONE}
    Setting multiple times    3    Test Setup

Test Teardown
    ${tc} =    Check Test Case    Use Defaults
    Should Be Equal    ${tc.teardown}    ${NONE}
    Setting multiple times    4    Test Teardown

Test Template
    ${tc} =    Check Test Case    Use Defaults
    Check Keyword Data     ${tc.kws[0]}    BuiltIn.Sleep    args=0.1s
    Setting multiple times    6    Test Template

Test Timeout
    ${tc} =    Check Test Case    Use Defaults
    Should Be Equal    ${tc.timeout}    ${NONE}
    Setting multiple times    11    Test Timeout

Test [Documentation]
    ${tc} =    Check Test Case    Test Settings
    Should Be Equal    ${tc.doc}    ${EMPTY}
    Setting multiple times in test case table    12    [Documentation]

Test [Tags]
    Check Test Tags    Test Settings
    Setting multiple times in test case table    13    [Tags]
    Setting multiple times in test case table    14    [Tags]

Test [Setup]
    ${tc} =    Check Test Case    Test Settings
    Should Be Equal    ${tc.setup}    ${NONE}
    Setting multiple times in test case table    15    [Setup]

Test [Teardown]
    ${tc} =    Check Test Case    Test Settings
    Should Be Equal    ${tc.teardown}    ${NONE}
    Setting multiple times in test case table    16    [Teardown]
    Setting multiple times in test case table    17    [Teardown]

Test [Template]
    ${tc} =    Check Test Case    Test Settings
    Check Keyword Data     ${tc.kws[0]}    BuiltIn.No Operation
    Setting multiple times in test case table    18    [Template]

Test [Timeout]
    ${tc} =    Check Test Case    Test Settings
    Should Be Equal    ${tc.timeout}    ${NONE}
    Setting multiple times in test case table    19    [Timeout]

Keyword [Arguments]
    ${tc} =    Check Test Case    Keyword Settings
    Check Keyword Data    ${tc.kws[0]}    Keyword Settings    assign=\${ret}
    Check Log Message    ${tc.kws[0].msgs[0]}    Arguments: [ \ ]    TRACE
    Setting multiple times in keyword table    20    [Arguments]

Keyword [Documentation]
    ${tc} =    Check Test Case    Keyword Settings
    Should Be Equal    ${tc.kws[0].doc}    ${EMPTY}
    Setting multiple times in keyword table    21    [Documentation]
    Setting multiple times in keyword table    22    [Documentation]

Keyword [Tags]
    ${tc} =    Check Test Case    Keyword Settings
    Should Be Empty    ${tc.kws[0].tags}
    Setting multiple times in keyword table    23    [Tags]

Keyword [Timeout]
    ${tc} =    Check Test Case    Keyword Settings
    Should Be Equal    ${tc.kws[0].timeout}    ${NONE}
    Setting multiple times in keyword table    24    [Timeout]
    Setting multiple times in keyword table    25    [Timeout]

Keyword [Return]
    ${tc} =    Check Test Case    Keyword Settings
    Check Log Message    ${tc.kws[0].msgs[1]}    Return: None    TRACE
    Check Log Message    ${tc.kws[0].msgs[2]}    \${ret} = None
    Setting multiple times in keyword table    26    [Return]
    Setting multiple times in keyword table    27    [Return]

*** Keywords ***
Setting multiple times
    [Arguments]    ${index}    ${setting}    @{extra}
    ${path} =    Normalize Path    ${DATADIR}/parsing/same_setting_multiple_times.robot
    ${message} =    Catenate
    ...    Error in file '${path}':
    ...    @{extra}
    ...    Setting '${setting}' used multiple times.
    Check Log Message      @{ERRORS}[${index}]    ${message}    ERROR

Setting multiple times in test case table
    [Arguments]    ${index}    ${setting}
    Setting multiple times    ${index}    ${setting}
    ...    Invalid syntax in test case 'Test Settings':

Setting multiple times in keyword table
    [Arguments]    ${index}    ${setting}
    Setting multiple times    ${index}    ${setting}
    ...    Invalid syntax in keyword 'Keyword Settings':

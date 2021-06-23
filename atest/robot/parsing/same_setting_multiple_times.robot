*** Settings ***
Suite Setup      Run Tests    -L TRACE    parsing/same_setting_multiple_times.robot
Resource         atest_resource.robot

*** Test Cases ***
Suite Documentation
    Should Be Equal    ${SUITE.doc}    S1
    Setting multiple times    0    3    Documentation

Suite Metadata
    Should Be Equal    ${SUITE.metadata['Foo']}    M2

Suite Setup
    Should Be Equal    ${SUITE.setup.name}    BuiltIn.Log Many
    Setting multiple times    1    7    Suite Setup

Suite Teardown
    Should Be Equal    ${SUITE.teardown.name}    BuiltIn.Comment
    Setting multiple times    2    9    Suite Teardown

Force and Default Tags
    Check Test Tags    Use Defaults    D1
    Setting multiple times    7     18    Force Tags
    Setting multiple times    8     19    Force Tags
    Setting multiple times    9     21    Default Tags
    Setting multiple times    10    22    Default Tags

Test Setup
    ${tc} =    Check Test Case    Use Defaults
    Should Be Equal    ${tc.setup.name}    BuiltIn.Log Many
    Setting multiple times    3    11    Test Setup

Test Teardown
    ${tc} =    Check Test Case    Use Defaults
    Teardown Should Not Be Defined     ${tc}
    Setting multiple times    4    13    Test Teardown

Test Template
    ${tc} =    Check Test Case    Use Defaults
    Check Keyword Data     ${tc.kws[0]}    BuiltIn.Log Many    args=Sleep, 0.1s
    Setting multiple times    6    16    Test Template

Test Timeout
    ${tc} =    Check Test Case    Use Defaults
    Should Be Equal    ${tc.timeout}    1 second
    Setting multiple times    11    24    Test Timeout

Test [Documentation]
    ${tc} =    Check Test Case    Test Settings
    Should Be Equal    ${tc.doc}    T1
    Setting multiple times    12    32    Documentation

Test [Tags]
    Check Test Tags    Test Settings
    Setting multiple times    13    34    Tags
    Setting multiple times    14    35    Tags

Test [Setup]
    ${tc} =    Check Test Case    Test Settings
    Should Be Equal    ${tc.setup.name}    BuiltIn.Log Many
    Setting multiple times    15    37    Setup

Test [Teardown]
    ${tc} =    Check Test Case    Test Settings
    Teardown Should Not Be Defined     ${tc}
    Setting multiple times    16    39    Teardown
    Setting multiple times    17    40    Teardown

Test [Template]
    ${tc} =    Check Test Case    Test Settings
    Check Keyword Data     ${tc.kws[0]}    BuiltIn.Log    args=No Operation
    Setting multiple times    18    42    Template

Test [Timeout]
    ${tc} =    Check Test Case    Test Settings
    Should Be Equal    ${tc.timeout}    2 seconds
    Setting multiple times    19    44    Timeout

Keyword [Arguments]
    ${tc} =    Check Test Case    Keyword Settings
    Check Keyword Data    ${tc.kws[0]}    Keyword Settings    assign=\${ret}    args=1, 2, 3    tags=K1
    Check Log Message    ${tc.kws[0].msgs[0]}    Arguments: [ \${a1}='1' | \${a2}='2' | \${a3}='3' ]    TRACE
    Setting multiple times    20    55    Arguments

Keyword [Documentation]
    ${tc} =    Check Test Case    Keyword Settings
    Should Be Equal    ${tc.kws[0].doc}    ${EMPTY}
    Setting multiple times    21    57    Documentation
    Setting multiple times    22    58    Documentation

Keyword [Tags]
    ${tc} =    Check Test Case    Keyword Settings
    Should Be True    list($tc.kws[0].tags) == ['K1']
    Setting multiple times    23    60    Tags

Keyword [Timeout]
    ${tc} =    Check Test Case    Keyword Settings
    Should Be Equal    ${tc.kws[0].timeout}    ${NONE}
    Setting multiple times    24    62    Timeout
    Setting multiple times    25    63    Timeout

Keyword [Return]
    ${tc} =    Check Test Case    Keyword Settings
    Check Log Message    ${tc.kws[0].msgs[1]}    Return: 'R0'    TRACE
    Check Log Message    ${tc.kws[0].msgs[2]}    \${ret} = R0
    Setting multiple times    26    66    Return
    Setting multiple times    27    67    Return
    Setting multiple times    28    68    Return

*** Keywords ***
Setting multiple times
    [Arguments]    ${index}    ${lineno}    ${setting}
    Error In File
    ...    ${index}    parsing/same_setting_multiple_times.robot    ${lineno}
    ...    Setting '${setting}' is allowed only once. Only the first value is used.

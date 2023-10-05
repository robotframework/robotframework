*** Settings ***
Suite Setup      Run Tests    -L TRACE    parsing/same_setting_multiple_times.robot
Resource         atest_resource.robot

*** Test Cases ***
Suite Documentation
    Should Be Equal    ${SUITE.doc}    S1

Suite Metadata
    Should Be Equal    ${SUITE.metadata['Foo']}    M2

Suite Setup
    Should Be Equal    ${SUITE.setup.full_name}    BuiltIn.Log Many

Suite Teardown
    Should Be Equal    ${SUITE.teardown.full_name}    BuiltIn.Comment

Force and Default Tags
    Check Test Tags    Use Defaults    D1

Test Setup
    ${tc} =    Check Test Case    Use Defaults
    Should Be Equal    ${tc.setup.full_name}    BuiltIn.Log Many

Test Teardown
    ${tc} =    Check Test Case    Use Defaults
    Teardown Should Not Be Defined     ${tc}

Test Template
    ${tc} =    Check Test Case    Use Defaults
    Check Keyword Data     ${tc.kws[0]}    BuiltIn.Log Many    args=Sleep, 0.1s

Test Timeout
    ${tc} =    Check Test Case    Use Defaults
    Should Be Equal    ${tc.timeout}    1 second

Test [Documentation]
    ${tc} =    Check Test Case    Test Settings
    Should Be Equal    ${tc.kws[0].type}    ERROR
    Should Be Equal    ${tc.kws[0].status}    FAIL
    Should Be Equal     ${tc.kws[0].values[0]}    [Documentation]

Test [Tags]
    Check Test Tags    Test Settings

Test [Setup]
    ${tc} =    Check Test Case    Test Settings
    Should Be Equal    ${tc.setup.full_name}    BuiltIn.Log Many

Test [Teardown]
    ${tc} =    Check Test Case    Test Settings
    Teardown Should Not Be Defined     ${tc}

Test [Template]
    ${tc} =    Check Test Case    Test Settings
    Check Keyword Data     ${tc.kws[7]}    BuiltIn.Log    args=No Operation

Test [Timeout]
    ${tc} =    Check Test Case    Test Settings
    Should Be Equal    ${tc.timeout}    2 seconds

Keyword [Arguments]
    ${tc} =    Check Test Case    Keyword Settings
    Check Keyword Data    ${tc.kws[0]}    Keyword Settings    assign=\${ret}    args=1, 2, 3    tags=K1    status=FAIL
    Check Log Message    ${tc.kws[0].msgs[0]}    Arguments: [ \${a1}='1' | \${a2}='2' | \${a3}='3' ]    TRACE

Keyword [Documentation]
    ${tc} =    Check Test Case    Keyword Settings
    Should Be Equal    ${tc.kws[0].doc}    ${EMPTY}

Keyword [Tags]
    ${tc} =    Check Test Case    Keyword Settings
    Should Be True    list($tc.kws[0].tags) == ['K1']

Keyword [Timeout]
    ${tc} =    Check Test Case    Keyword Settings
    Should Be Equal    ${tc.kws[0].timeout}    ${NONE}

Keyword [Return]
    Check Test Case    Keyword Settings

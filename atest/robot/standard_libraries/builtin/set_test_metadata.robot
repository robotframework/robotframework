*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    standard_libraries/builtin/set_test_metadata.robot
Resource          atest_resource.robot

*** Test Cases ***
Set new value
    Metadata should have value    New metadata    Set in test
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc[0, 0]}
    ...    Set test metadata 'New metadata' to value 'Set in test'.

Override existing value
    Metadata should have value    Initial    New value
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc[0, 0]}
    ...    Set test metadata 'Initial' to value 'New value'.

Names are case and space insensitive
    Metadata should have value    My Name    final value
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc[1, 0]}
    ...    Set test metadata 'MYname' to value 'final value'.

Append to value
    Metadata should have value    To Append    Original is continued \n\ntwice!
    Metadata should have value    Version    1.0/2.0/3.0
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc[0, 0]}
    ...    Set test metadata 'To Append' to value 'Original'.
    Check Log Message    ${tc[4, 0]}
    ...    Set test metadata 'TOAPPEND' to value 'Original is continued \n\ntwice!'.
    Check Log Message    ${tc[10, 0]}
    ...    Set test metadata 'ver sion' to value '1.0/2.0/3.0'.

Non-ASCII and non-string names and values
    Metadata should have value    42    1 päivä
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc[0, 0]}
    ...    Set test metadata '42' to value '1'.
    Check Log Message    ${tc[2, 0]}
    ...    Set test metadata '42' to value '1 päivä'.

Modifying \${TEST METADATA} has no effect also after setting metadata
    Check Test Case    ${TESTNAME}
    Metadata should have value    Cannot be    set otherwise

Set Task Metadata as alias for Set Test Metadata
    Metadata should have value    Task    Value is continued
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc[0, 0]}
    ...    Set test metadata 'Task' to value 'Value'.

Set in test setup
    Metadata should have value    Setup    Value

Set in test teardown
    Metadata should have value    Teardown    Another value

Metadata is test specific
    ${tc} =    Check Test Case    ${TESTNAME}
    Should Be Empty    ${tc.metadata}

*** Keywords ***
Metadata should have value
    [Arguments]    ${name}    ${value}
    ${tc} =    Check Test Case    ${TESTNAME}
    Should Be Equal    ${tc.metadata['${name}']}    ${value}

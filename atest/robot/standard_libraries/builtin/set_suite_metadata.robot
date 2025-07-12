*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    standard_libraries/builtin/set_suite_metadata.robot misc/pass_and_fail.robot
Resource          atest_resource.robot

*** Test Cases ***
Set new value
    Metadata should have value    New metadata    Set in test
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc[0, 0]}
    ...    Set suite metadata 'New metadata' to value 'Set in test'.

Override existing value
    Metadata should have value    Initial    New value
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc[0, 0]}
    ...    Set suite metadata 'Initial' to value 'New value'.

Names are case and space insensitive
    Metadata should have value    My Name    final value
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc[1, 0]}
    ...    Set suite metadata 'MYname' to value 'final value'.

Append to value
    Metadata should have value    To Append    Original is continued \n\ntwice!
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc[0, 0]}
    ...    Set suite metadata 'To Append' to value 'Original'.
    Check Log Message    ${tc[2, 0]}
    ...    Set suite metadata 'toappend' to value 'Original is continued'.
    Check Log Message    ${tc[4, 0]}
    ...    Set suite metadata 'TOAPPEND' to value 'Original is continued \n\ntwice!'.
    Check Log Message    ${tc[6, 0]}
    ...    Set suite metadata 'Version' to value '1.0'.
    Check Log Message    ${tc[8, 0]}
    ...    Set suite metadata 'version' to value '1.0/2.0'.
    Check Log Message    ${tc[10, 0]}
    ...    Set suite metadata 'ver sion' to value '1.0/2.0/3.0'.

Set top-level suite metadata
    Metadata should have value    New metadata    Metadata for top level suite    top=yes
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc[0, 0]}
    ...    Set suite metadata 'New metadata' to value 'Metadata for'.
    Check Log Message    ${tc[1, 0]}
    ...    Set suite metadata 'newmetadata' to value 'Metadata for top level suite'.
    Metadata should have value    Separator    2top**level    top=yes
    Check Log Message    ${tc[3, 0]}
    ...    Set suite metadata 'Separator' to value '2'.
    Check Log Message    ${tc[4, 0]}
    ...    Set suite metadata 'Separator' to value '2top'.
    Check Log Message    ${tc[5, 0]}
    ...    Set suite metadata 'Separator' to value '2top**level'.

Non-ASCII and non-string names and values
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc[0, 0]}
    ...    Set suite metadata '42' to value '1'.
    Check Log Message    ${tc[2, 0]}
    ...    Set suite metadata '42' to value '1 päivä'.

Modifying \${SUITE METADATA} has no effect also after setting metadata
    Check Test Case    ${TESTNAME}
    Metadata should have value    Cannot be   set otherwise

Set in suite setup
    Metadata should have value    Setup    Value

Set in suite teardown
    Metadata should have value    Teardown    Another value

*** Keywords ***
Metadata should have value
    [Arguments]    ${name}    ${value}    ${top}=
    ${suite} =    Set Variable If    "${top}"    ${SUITE}    ${SUITE.suites[0]}
    Should Be Equal    ${suite.metadata['${name}']}    ${value}

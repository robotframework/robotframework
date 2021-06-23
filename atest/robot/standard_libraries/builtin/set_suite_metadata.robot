*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    standard_libraries/builtin/set_suite_metadata.robot misc/pass_and_fail.robot
Resource          atest_resource.robot

*** Test Cases ***
Set new value
    Metadata should have value    New metadata    Set in test
    ${tc} =    Check test case    ${TESTNAME}
    Check log message    ${tc.kws[0].msgs[0]}
    ...    Set suite metadata 'New metadata' to value 'Set in test'.

Override existing value
    Metadata should have value    Initial    New value
    ${tc} =    Check test case    ${TESTNAME}
    Check log message    ${tc.kws[0].msgs[0]}
    ...    Set suite metadata 'Initial' to value 'New value'.

Names are case and space insensitive
    Metadata should have value    My Name    final value
    ${tc} =    Check test case    ${TESTNAME}
    Check log message    ${tc.kws[1].msgs[0]}
    ...    Set suite metadata 'MYname' to value 'final value'.

Append to value
    Metadata should have value    To Append    Original is continued \n\ntwice!
    ${tc} =    Check test case    ${TESTNAME}
    Check log message    ${tc.kws[0].msgs[0]}
    ...    Set suite metadata 'To Append' to value 'Original'.
    Check log message    ${tc.kws[2].msgs[0]}
    ...    Set suite metadata 'toappend' to value 'Original is continued'.
    Check log message    ${tc.kws[4].msgs[0]}
    ...    Set suite metadata 'TOAPPEND' to value 'Original is continued \n\ntwice!'.

Set top-level suite metadata
    Metadata should have value    New metadata    Metadata for top level suite    top=yes
    ${tc} =    Check test case    ${TESTNAME}
    Check log message    ${tc.kws[0].msgs[0]}
    ...    Set suite metadata 'New metadata' to value 'Metadata for'.
    Check log message    ${tc.kws[1].msgs[0]}
    ...    Set suite metadata 'newmetadata' to value 'Metadata for top level suite'.

Non-ASCII and non-string names and values
    ${tc} =    Check test case    ${TESTNAME}
    Check log message    ${tc.kws[0].msgs[0]}
    ...    Set suite metadata '42' to value '1'.
    Check log message    ${tc.kws[2].msgs[0]}
    ...    Set suite metadata '42' to value '1 päivä'.

Modifying \${SUITE METADATA} has no effect also after setting metadata
    Check test case    ${TESTNAME}
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

*** Settings ***
Suite Setup       Run Tests    --dryrun    cli/dryrun/dryrun.robot cli/dryrun/more_tests.robot
Test Teardown     Last keyword should have been validated
Resource          atest_resource.robot

*** Test Cases ***
Passing keywords
    ${tc}=    Check Test Case    ${TESTNAME}
    Should have correct number of keywords    ${tc}    4
    Check Keyword Data    ${tc.kws[0]}    BuiltIn.Log    status=NOT_RUN    args=Hello from test
    Check Keyword Data    ${tc.kws[1]}    OperatingSystem.List Directory    status=NOT_RUN    assign=\${contents}    args=.
    Check Keyword Data    ${tc.kws[2]}    resource.Simple UK
    Check Keyword Data    ${tc.kws[2].kws[0]}    BuiltIn.Log    status=NOT_RUN    args=Hello from UK

Keywords with embedded arguments
    ${tc}=    Check Test Case    ${TESTNAME}
    Should have correct number of keywords    ${tc}    3
    Check Keyword Data    ${tc.kws[0]}    Embedded arguments here
    Check Keyword Data    ${tc.kws[0].kws[0]}    BuiltIn.No Operation    status=NOT_RUN
    Check Keyword Data    ${tc.kws[1]}    Embedded args rock here
    Check Keyword Data    ${tc.kws[1].kws[0]}    BuiltIn.No Operation    status=NOT_RUN

Library keyword with embedded arguments
    ${tc}=    Check Test Case    ${TESTNAME}
    Should have correct number of keywords    ${tc}    2
    Check Keyword Data    ${tc.kws[0]}    EmbeddedArgs.Log 42 times    status=NOT_RUN

Keywords that would fail
    ${tc}=    Check Test Case    ${TESTNAME}
    Should have correct number of keywords    ${tc}    3
    Check Keyword Data    ${tc.kws[0]}    BuiltIn.Fail    status=NOT_RUN    args=Not actually executed so won't fail.
    Check Keyword Data    ${tc.kws[1]}    resource.Fail In UK
    Should have correct number of keywords    ${tc.kws[1]}    2
    Check Keyword Data    ${tc.kws[1].kws[0]}    BuiltIn.Fail    status=NOT_RUN    args=
    Check Keyword Data    ${tc.kws[1].kws[1]}    BuiltIn.Fail    status=NOT_RUN    args=And again

Scalar variables are not checked in keyword arguments
    [Documentation]    Variables are too often set somehow dynamically that we cannot expect them to always exist.
    ${tc}=    Check Test Case    ${TESTNAME}
    Check Keyword Data    ${tc.kws[0]}    BuiltIn.Log    status=NOT_RUN    args=\${TESTNAME}
    Check Keyword Data    ${tc.kws[1]}    BuiltIn.Log    status=NOT_RUN    args=\${this does not exist}

List variables are not checked in keyword arguments
    [Documentation]    See the doc of the previous test
    Check Test Case    ${TESTNAME}

Variables are not checked in when arguments are embedded
    [Documentation]    See the doc of the previous test
    ${tc}=    Check Test Case    ${TESTNAME}
    Check Keyword Data    ${tc.kws[0]}    Embedded \${TESTNAME} here
    Check Keyword Data    ${tc.kws[0].kws[0]}    BuiltIn.No Operation    status=NOT_RUN
    Check Keyword Data    ${tc.kws[1]}    Embedded \${nonex} here
    Check Keyword Data    ${tc.kws[1].kws[0]}    BuiltIn.No Operation    status=NOT_RUN

Setup/teardown with non-existing variable is ignored
    ${tc} =    Check Test Case    ${TESTNAME}
    Should Be Equal    ${SUITE.setup}    ${NONE}
    Should Be Equal    ${tc.setup}    ${NONE}
    Should Be Equal    ${tc.teardown}    ${NONE}

Setup/teardown with existing variable is resolved and executed
    ${tc} =    Check Test Case    ${TESTNAME}
    Should Be Equal    ${tc.setup.name}    BuiltIn.No Operation
    Should Be Equal    ${tc.teardown.name}    Teardown
    ${args} =    Create List    \${nonex arg}
    Lists Should Be Equal    ${tc.teardown.args}    ${args}
    Lists Should Be Equal    ${tc.teardown.keywords[0].name}    BuiltIn.Log

User keyword return value
    Check Test Case    ${TESTNAME}

Test Setup and Teardown
    ${tc}=    Check Test Case    ${TESTNAME}
    Should have correct number of keywords    ${tc}    2
    Should Be Equal    ${tc.setup.name}    BuiltIn.Log
    Should Be Equal    ${tc.teardown.name}    Does not exist

Keyword Teardown
    ${tc}=    Check Test Case    ${TESTNAME}
    Should have correct number of keywords    ${tc}    2
    Should Be Equal    ${tc.kws[0].kws[1].name}    Does not exist

For Loops
    ${tc}=    Check Test Case    ${TESTNAME}
    Should have correct number of keywords    ${tc}    4
    Should have correct number of keywords    ${tc.kws[0]}    1
    Should have correct number of keywords    ${tc.kws[0].kws[0]}    2
    Should have correct number of keywords    ${tc.kws[1]}    3
    Should have correct number of keywords    ${tc.kws[1].kws[1]}    1

Non-existing keyword name
    Check Test Case    ${TESTNAME}

Invalid syntax in UK
    Check Test Case    ${TESTNAME}
    ${source} =    Normalize Path    ${DATADIR}/cli/dryrun/dryrun.robot
    ${message} =    Catenate
    ...    Error in test case file '${source}':
    ...    Creating keyword 'Invalid Syntax UK' failed:
    ...    Invalid argument specification:
    ...    Invalid argument syntax '${arg'.
    Check Log Message    ${ERRORS[0]}    ${message}    ERROR

Multiple Failures
    Check Test Case    ${TESTNAME}

Avoid keyword in dry-run
    ${tc} =    Check Test Case    ${TESTNAME}
    Keyword should have been skipped with tag    ${tc.kws[0]}    Keyword not run in dry-run    robot:no-dry-run
    Keyword should have been skipped with tag    ${tc.kws[1]}    Another keyword not run in dry-run    ROBOT: no-dry-run
    Keyword should have been skipped with tag    ${tc.kws[2].kws[0]}    Keyword not run in dry-run    robot:no-dry-run
    Keyword should have been skipped with tag    ${tc.kws[2].kws[1]}    Another keyword not run in dry-run    ROBOT: no-dry-run
    Keyword should have been validated    ${tc.kws[2].kws[2]}
    Keyword should have been validated    ${tc.kws[3]}

Invalid imports
    Import should have failed    1    cli/dryrun/dryrun.robot
    ...    Importing test library 'DoesNotExist' failed: *Error: *
    Import should have failed    2    cli/dryrun/dryrun.robot
    ...    Variable file 'wrong_path.py' does not exist.
    ...    traceback=
    Import should have failed    3    cli/dryrun/dryrun.robot
    ...    Resource file 'NonExisting.robot' does not exist.
    ...    traceback=
    [Teardown]    NONE

Test from other suite
    Check Test Case    Some Other Test
    [Teardown]    NONE

*** Keywords ***
Should have correct number of keywords
    [Arguments]    ${test or uk}    ${exp number of kws}
    Log    ${test or uk.kws}
    Should Be Equal As Integers    ${test or uk.kw_count}    ${exp number of kws}

Keyword should have been skipped with tag
    [Arguments]    ${kw}    ${name}    ${tags}
    Check Keyword Data    ${kw}    ${name}    status=PASS    tags=${tags}
    Should Be Empty    ${kw.kws}

Keyword should have been validated
    [Arguments]    ${kw}
    Check Keyword Data    ${kw}    This is validated
    Check Keyword Data    ${kw.kws[0]}    BuiltIn.Log    status=NOT_RUN    args=This is validated

Last keyword should have been validated
    ${tc} =    Get test case    ${TEST NAME}
    Keyword should have been validated    ${tc.kws[-1]}

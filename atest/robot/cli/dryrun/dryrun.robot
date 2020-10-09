*** Settings ***
Suite Setup       Run Tests    --dryrun    cli/dryrun/dryrun.robot cli/dryrun/more_tests.robot
Test Teardown     Last keyword should have been validated
Resource          dryrun_resource.robot

*** Test Cases ***
Passing keywords
    ${tc}=    Check Test Case    ${TESTNAME}
    Length Should Be      ${tc.kws}              4
    Check Keyword Data    ${tc.kws[0]}           BuiltIn.Log    status=NOT_RUN    args=Hello from test
    Check Keyword Data    ${tc.kws[1]}           OperatingSystem.List Directory    status=NOT_RUN    assign=\${contents}    args=.
    Check Keyword Data    ${tc.kws[2]}           resource.Simple UK
    Check Keyword Data    ${tc.kws[2].kws[0]}    BuiltIn.Log    status=NOT_RUN    args=Hello from UK

Keywords with embedded arguments
    ${tc}=    Check Test Case    ${TESTNAME}
    Length Should Be      ${tc.kws}              3
    Check Keyword Data    ${tc.kws[0]}           Embedded arguments here
    Check Keyword Data    ${tc.kws[0].kws[0]}    BuiltIn.No Operation    status=NOT_RUN
    Check Keyword Data    ${tc.kws[1]}           Embedded args rock here
    Check Keyword Data    ${tc.kws[1].kws[0]}    BuiltIn.No Operation    status=NOT_RUN

Library keyword with embedded arguments
    ${tc}=    Check Test Case    ${TESTNAME}
    Length Should Be      ${tc.kws}              2
    Check Keyword Data    ${tc.kws[0]}           EmbeddedArgs.Log 42 times    status=NOT_RUN

Keywords that would fail
    ${tc}=    Check Test Case    ${TESTNAME}
    Length Should Be      ${tc.kws}              3
    Check Keyword Data    ${tc.kws[0]}           BuiltIn.Fail    status=NOT_RUN    args=Not actually executed so won't fail.
    Check Keyword Data    ${tc.kws[1]}           resource.Fail In UK
    Length Should Be      ${tc.kws[1].kws}       2
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
    Check Keyword Data    ${tc.setup}    BuiltIn.No Operation    status=NOT_RUN    type=setup
    Check Keyword Data    ${tc.teardown}    Teardown    args=\${nonex arg}    type=teardown
    Check Keyword Data    ${tc.teardown.keywords[0]}    BuiltIn.Log    args=\${arg}    status=NOT_RUN

User keyword return value
    Check Test Case    ${TESTNAME}

Non-existing variable in user keyword return value
    Check Test Case    ${TESTNAME}

Test Setup and Teardown
    ${tc}=    Check Test Case    ${TESTNAME}
    Length Should Be      ${tc.kws}         2
    Check Keyword Data    ${tc.setup}       BuiltIn.Log    args=Hello Setup    status=NOT_RUN    type=setup
    Check Keyword Data    ${tc.teardown}    Does not exist    status=FAIL    type=teardown

Keyword Teardown
    ${tc}=    Check Test Case    ${TESTNAME}
    Length Should Be      ${tc.kws}              2
    Check Keyword Data    ${tc.kws[0].kws[-1]}   Does not exist    status=FAIL    type=teardown

Keyword teardown with non-existing variable is ignored
    Check Test Case    ${TESTNAME}

Keyword teardown with existing variable is resolved and executed
    ${tc}=    Check Test Case    ${TESTNAME}
    Check Keyword Data    ${tc.kws[0].kws[-1]}    Teardown    args=\${I DO NOT EXIST}    type=teardown
    Check Keyword Data    ${tc.kws[0].kws[-1].kws[0]}    BuiltIn.Log    args=\${arg}    status=NOT_RUN

Non-existing keyword name
    Check Test Case    ${TESTNAME}

Invalid syntax in UK
    Check Test Case    ${TESTNAME}
    ${source} =    Normalize Path    ${DATADIR}/cli/dryrun/dryrun.robot
    ${message} =    Catenate
    ...    Error in test case file '${source}':
    ...    Creating keyword 'Invalid Syntax UK' failed:
    ...    Invalid argument specification:
    ...    Invalid argument syntax '\${arg'.
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
    Error in file    1    cli/dryrun/dryrun.robot    7
    ...    Importing test library 'DoesNotExist' failed: *Error: *
    Error in file    2    cli/dryrun/dryrun.robot    8
    ...    Variable file 'wrong_path.py' does not exist.
    Error in file    3    cli/dryrun/dryrun.robot    9
    ...    Resource file 'NonExisting.robot' does not exist.
    [Teardown]    NONE

Test from other suite
    Check Test Case    Some Other Test
    [Teardown]    NONE

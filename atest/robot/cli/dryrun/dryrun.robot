*** Settings ***
Suite Setup       Run Tests    --dryrun    cli/dryrun/dryrun.robot cli/dryrun/more_tests.robot
Test Teardown     Last keyword should have been validated
Resource          dryrun_resource.robot

*** Test Cases ***
Passing keywords
    ${tc}=    Check Test Case    ${TESTNAME}
    Length Should Be      ${tc.kws}              4
    Check Keyword Data    ${tc.kws[0]}           BuiltIn.Log    status=NOT RUN    args=Hello from test
    Check Keyword Data    ${tc.kws[1]}           OperatingSystem.List Directory    status=NOT RUN    assign=\${contents}    args=.
    Check Keyword Data    ${tc.kws[2]}           resource.Simple UK
    Check Keyword Data    ${tc.kws[2].kws[0]}    BuiltIn.Log    status=NOT RUN    args=Hello from UK

Keywords with embedded arguments
    ${tc}=    Check Test Case    ${TESTNAME}
    Length Should Be      ${tc.kws}              5
    Check Keyword Data    ${tc.kws[0]}           Embedded arguments here
    Check Keyword Data    ${tc.kws[0].kws[0]}    BuiltIn.No Operation    status=NOT RUN
    Check Keyword Data    ${tc.kws[1]}           Embedded args rock here
    Check Keyword Data    ${tc.kws[1].kws[0]}    BuiltIn.No Operation    status=NOT RUN
    Check Keyword Data    ${tc.kws[2]}           Some embedded and normal args    args=42
    Check Keyword Data    ${tc.kws[2].kws[0]}    BuiltIn.No Operation    status=NOT RUN
    Check Keyword Data    ${tc.kws[3]}           Some embedded and normal args    args=\${does not exist}
    Check Keyword Data    ${tc.kws[3].kws[0]}    BuiltIn.No Operation    status=NOT RUN

Library keyword with embedded arguments
    ${tc}=    Check Test Case    ${TESTNAME}
    Length Should Be      ${tc.kws}              2
    Check Keyword Data    ${tc.kws[0]}           EmbeddedArgs.Log 42 times    status=NOT RUN

Keywords that would fail
    ${tc}=    Check Test Case    ${TESTNAME}
    Length Should Be      ${tc.kws}              3
    Check Keyword Data    ${tc.kws[0]}           BuiltIn.Fail    status=NOT RUN    args=Not actually executed so won't fail.
    Check Keyword Data    ${tc.kws[1]}           resource.Fail In UK
    Length Should Be      ${tc.kws[1].kws}       2
    Check Keyword Data    ${tc.kws[1].kws[0]}    BuiltIn.Fail    status=NOT RUN    args=
    Check Keyword Data    ${tc.kws[1].kws[1]}    BuiltIn.Fail    status=NOT RUN    args=And again

Scalar variables are not checked in keyword arguments
    [Documentation]    Variables are too often set somehow dynamically that we cannot expect them to always exist.
    ${tc}=    Check Test Case    ${TESTNAME}
    Check Keyword Data    ${tc.kws[0]}    BuiltIn.Log    status=NOT RUN    args=\${TESTNAME}
    Check Keyword Data    ${tc.kws[1]}    BuiltIn.Log    status=NOT RUN    args=\${this does not exist}

List variables are not checked in keyword arguments
    [Documentation]    See the doc of the previous test
    Check Test Case    ${TESTNAME}

Dict variables are not checked in keyword arguments
    [Documentation]    See the doc of the previous test
    Check Test Case    ${TESTNAME}

Variables are not checked in when arguments are embedded
    [Documentation]    See the doc of the previous test
    ${tc}=    Check Test Case    ${TESTNAME}
    Check Keyword Data    ${tc.kws[0]}    Embedded \${TESTNAME} here
    Check Keyword Data    ${tc.kws[0].kws[0]}    BuiltIn.No Operation    status=NOT RUN
    Check Keyword Data    ${tc.kws[1]}    Embedded \${nonex} here
    Check Keyword Data    ${tc.kws[1].kws[0]}    BuiltIn.No Operation    status=NOT RUN

Setup/teardown with non-existing variable is ignored
    ${tc} =    Check Test Case    ${TESTNAME}
    Setup Should Not Be Defined     ${SUITE}
    Setup Should Not Be Defined     ${tc}
    Teardown Should Not Be Defined     ${tc}

Setup/teardown with existing variable is resolved and executed
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Keyword Data    ${tc.setup}    BuiltIn.No Operation    status=NOT RUN    type=SETUP
    Check Keyword Data    ${tc.teardown}    Teardown    args=\${nonex arg}    type=TEARDOWN
    Check Keyword Data    ${tc.teardown.body[0]}    BuiltIn.Log    args=\${arg}    status=NOT RUN

User keyword return value
    Check Test Case    ${TESTNAME}

Non-existing variable in user keyword return value
    Check Test Case    ${TESTNAME}

Test Setup and Teardown
    ${tc}=    Check Test Case    ${TESTNAME}
    Length Should Be      ${tc.kws}         2
    Check Keyword Data    ${tc.setup}       BuiltIn.Log    args=Hello Setup    status=NOT RUN    type=SETUP
    Check Keyword Data    ${tc.teardown}    Does not exist    status=FAIL    type=TEARDOWN

Keyword Teardown
    ${tc}=    Check Test Case    ${TESTNAME}
    Length Should Be      ${tc.kws}              2
    Check Keyword Data    ${tc.kws[0].teardown}   Does not exist    status=FAIL    type=TEARDOWN

Keyword teardown with non-existing variable is ignored
    Check Test Case    ${TESTNAME}

Keyword teardown with existing variable is resolved and executed
    ${tc}=    Check Test Case    ${TESTNAME}
    Check Keyword Data    ${tc.kws[0].teardown}    Teardown    args=\${I DO NOT EXIST}    type=TEARDOWN
    Check Keyword Data    ${tc.kws[0].teardown.kws[0]}    BuiltIn.Log    args=\${arg}    status=NOT RUN

Non-existing keyword name
    Check Test Case    ${TESTNAME}

Invalid syntax in UK
    Check Test Case    ${TESTNAME}
    Error In File    0    cli/dryrun/dryrun.robot    167
    ...    SEPARATOR=\n
    ...    Creating keyword 'Invalid Syntax UK' failed: Invalid argument specification: Multiple errors:
    ...    - Invalid argument syntax '\${oops'.
    ...    - Non-default argument after default arguments.

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
    ...    Importing library 'DoesNotExist' failed: *Error: *
    Error in file    2    cli/dryrun/dryrun.robot    8
    ...    Variable file 'wrong_path.py' does not exist.
    Error in file    3    cli/dryrun/dryrun.robot    9
    ...    Resource file 'NonExisting.robot' does not exist.
    [Teardown]    NONE

Test from other suite
    Check Test Case    Some Other Test
    [Teardown]    NONE

*** Settings ***
Documentation     Execution should continue after normal failures in teardowns.
Suite Setup       Run Tests    ${EMPTY}    running/failures_in_teardown.robot
Resource          atest_resource.robot

*** Test Cases ***
One Failure
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc.teardown.kws[1].msgs[0]}    This should be executed

Multiple Failures
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc.teardown.kws[2].msgs[0]}    This should also be executed

Failure When Setting Variables
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc.teardown.kws[0].msgs[0]}    \${ret} = None
    Check Log Message    ${tc.teardown.kws[0].msgs[1]}    Return values is None    FAIL

Failure In For Loop
    Check Test Case    ${TESTNAME}

Execution Continues After Test Timeout
    ${tc} =    Check Test Case    ${TESTNAME}
    Elapsed Time Should Be Valid    ${tc.elapsed_time}    minimum=0.3

Execution Stops After Keyword Timeout
    ${tc} =    Check Test Case    ${TESTNAME}
    Length Should Be    ${tc.teardown.kws}    2
    Should Be Equal    ${tc.teardown.kws[-1].status}    NOT RUN

Execution Continues After Keyword Timeout Occurs In Executed Keyword
    ${tc} =    Check Test Case    ${TESTNAME}
    Length Should Be    ${tc.teardown.body}                      2
    Length Should Be    ${tc.teardown.body[0].body}              2
    Should Be Equal     ${tc.teardown.body[0].body[0].status}    FAIL
    Should Be Equal     ${tc.teardown.body[0].body[1].status}    NOT RUN
    Should Be Equal     ${tc.teardown.body[0].status}            FAIL
    Should Be Equal     ${tc.teardown.body[1].status}            FAIL

Execution Continues If Variable Does Not Exist
    ${tc} =    Check Test Case    ${TESTNAME}
    Length Should Be    ${tc.teardown.kws}    3

Execution Continues After Keyword Errors
    ${tc} =    Check Test Case    ${TESTNAME}
    Length Should Be    ${tc.teardown.kws}    3

Execution Stops After Syntax Error
    ${tc} =    Check Test Case    ${TESTNAME}
    Length Should Be    ${tc.teardown.kws}    2
    Should Be Equal    ${tc.teardown.kws[-1].status}    NOT RUN

Fatal Error
    ${tc} =    Check Test Case    ${TESTNAME} 1
    Length Should Be    ${tc.teardown.kws}    2
    Should Be Equal    ${tc.teardown.kws[-1].status}    NOT RUN
    Check Test Case    ${TESTNAME} 2

Suite Teardown Is Executed Fully
    ${td} =    Set Variable    ${SUITE.teardown}
    Check Log Message    ${td.kws[0].msgs[0]}    Suite Message 1    FAIL
    Check Log Message    ${td.kws[1].msgs[0]}    Suite Message 2 (with ∏ön ÄßÇïï €§)    FAIL
    Check Log Message    ${td.kws[2].msgs[0]}    Variable '\${it is ok not to exist}' not found.    FAIL
    Check Log Message    ${td.kws[3].msgs[0]}    This should be executed
    ${msg} =    Catenate    SEPARATOR=\n\n
    ...    Suite teardown failed:\nSeveral failures occurred:
    ...    1) Suite Message 1
    ...    2) Suite Message 2 (with ∏ön ÄßÇïï €§)
    ...    3) Variable '\${it is ok not to exist}' not found.
    Should Be Equal    ${SUITE.message}    ${msg}

Suite Teardown Should Stop At Fatal Error
    Run Tests    ${EMPTY}    running/fatal_error_in_suite_teardown.robot
    ${ts} =    Get Test Suite    fatal error in suite teardown
    Length Should Be    ${ts.teardown.kws}    2
    Should Be Equal    ${ts.teardown.kws[-1].status}    NOT RUN

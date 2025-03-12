*** Settings ***
Documentation     Execution should continue after normal failures in teardowns.
Suite Setup       Run Tests    ${EMPTY}    running/failures_in_teardown.robot
Resource          atest_resource.robot

*** Test Cases ***
One Failure
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc.teardown[1, 0]}    This should be executed

Multiple Failures
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc.teardown[2, 0]}    This should also be executed

Failure When Setting Variables
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc.teardown[0, 0]}    \${ret} = None
    Check Log Message    ${tc.teardown[0, 1]}    Return values is None    FAIL

Failure In For Loop
    Check Test Case    ${TESTNAME}

Execution Continues After Test Timeout
    ${tc} =    Check Test Case    ${TESTNAME}
    Elapsed Time Should Be Valid    ${tc.elapsed_time}    minimum=0.3

Execution Stops After Keyword Timeout
    ${tc} =    Check Test Case    ${TESTNAME}
    Length Should Be    ${tc.teardown.body}              2
    Should Be Equal     ${tc.teardown[-1].status}        NOT RUN

Execution continues if executed keyword fails for keyword timeout
    ${tc} =    Check Test Case    ${TESTNAME}
    Length Should Be    ${tc.teardown.body}              2
    Should Be Equal     ${tc.teardown.body[0].status}    FAIL
    Should Be Equal     ${tc.teardown.body[1].status}    FAIL
    Length Should Be    ${tc.teardown.body[0].body}      2
    Should Be Equal     ${tc.teardown[0, 0].status}      FAIL
    Check Log Message   ${tc.teardown}[0, 0, 0]          Keyword timeout 42 milliseconds exceeded.    FAIL
    Should Be Equal     ${tc.teardown[0, 1].status}      NOT RUN
    Length Should Be    ${tc.teardown.body[1].body}      1
    Check Log Message   ${tc.teardown}[1, 0]             This should be executed    FAIL

Execution stops after keyword timeout if keyword uses WUKS
    ${tc} =    Check Test Case    ${TESTNAME}
    Length Should Be    ${tc.teardown.body}               2
    Should Be Equal     ${tc.teardown.body[0].status}     FAIL
    Should Be Equal     ${tc.teardown.body[1].status}     NOT RUN
    Length Should Be    ${tc.teardown.body[0].body}       2
    Should Be Equal     ${tc.teardown[0, 0].status}       FAIL
    Should Be Equal     ${tc.teardown[0, 1].status}       FAIL
    Length Should Be    ${tc.teardown[0, 0].body}         2
    Should Be Equal     ${tc.teardown[0, 0, 0].status}    PASS
    Should Be Equal     ${tc.teardown[0, 0, 1].status}    FAIL
    Check Log Message   ${tc.teardown}[0, 0, 1, 0]        Failing!    FAIL
    Length Should Be    ${tc.teardown[0, 1].body}         2
    Should Be Equal     ${tc.teardown[0, 1, 0].status}    FAIL
    Check Log Message   ${tc.teardown}[0, 1, 0, 0]        Keyword timeout 100 milliseconds exceeded.    FAIL
    Should Be Equal     ${tc.teardown[0, 1, 1].status}    NOT RUN

Execution Continues If Variable Does Not Exist
    ${tc} =    Check Test Case    ${TESTNAME}
    Length Should Be    ${tc.teardown.body}    3

Execution Continues After Keyword Errors
    ${tc} =    Check Test Case    ${TESTNAME}
    Length Should Be    ${tc.teardown.body}    3

Execution Stops After Syntax Error
    ${tc} =    Check Test Case    ${TESTNAME}
    Length Should Be    ${tc.teardown.body}          2
    Should Be Equal     ${tc.teardown[-1].status}    NOT RUN

Fatal Error
    ${tc} =    Check Test Case    ${TESTNAME} 1
    Length Should Be    ${tc.teardown.body}          2
    Should Be Equal     ${tc.teardown[-1].status}    NOT RUN
    Check Test Case     ${TESTNAME} 2

Suite Teardown Is Executed Fully
    ${td} =    Set Variable    ${SUITE.teardown}
    Check Log Message    ${td[0, 0]}    Suite Message 1    FAIL
    Check Log Message    ${td[1, 0]}    Suite Message 2 (with ∏ön ÄßÇïï €§)    FAIL
    Check Log Message    ${td[2, 0]}    Variable '\${it is ok not to exist}' not found.    FAIL
    Check Log Message    ${td[3, 0]}    This should be executed
    ${msg} =    Catenate    SEPARATOR=\n\n
    ...    Suite teardown failed:\nSeveral failures occurred:
    ...    1) Suite Message 1
    ...    2) Suite Message 2 (with ∏ön ÄßÇïï €§)
    ...    3) Variable '\${it is ok not to exist}' not found.
    Should Be Equal    ${SUITE.message}    ${msg}

Suite Teardown Should Stop At Fatal Error
    Run Tests    ${EMPTY}    running/fatal_error_in_suite_teardown.robot
    ${ts} =    Get Test Suite    fatal error in suite teardown
    Length Should Be    ${ts.teardown.body}    2
    Should Be Equal     ${ts.teardown[-1].status}    NOT RUN

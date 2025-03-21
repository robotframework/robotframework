*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    standard_libraries/process/robot_timeouts.robot
Resource          atest_resource.robot

*** Test Cases ***
Test timeout
    ${tc} =    Check Test Case    ${TESTNAME}
    Should Be True    ${tc.elapsed_time.total_seconds()} < 1
    Check Log Message    ${tc[0][1]}    Waiting for process to complete.
    Check Log Message    ${tc[0][2]}    Test timeout exceeded.
    Check Log Message    ${tc[0][3]}    Forcefully killing process.
    Check Log Message    ${tc[0][4]}    Test timeout 500 milliseconds exceeded.    FAIL

Keyword timeout
    ${tc} =    Check Test Case    ${TESTNAME}
    Should Be True    ${tc.elapsed_time.total_seconds()} < 1
    Check Log Message    ${tc[0][1][0]}    Waiting for process to complete.
    Check Log Message    ${tc[0][1][1]}    Keyword timeout exceeded.
    Check Log Message    ${tc[0][1][2]}    Forcefully killing process.
    Check Log Message    ${tc[0][1][3]}    Keyword timeout 500 milliseconds exceeded.    FAIL

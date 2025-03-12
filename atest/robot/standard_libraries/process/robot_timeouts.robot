*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    standard_libraries/process/robot_timeouts.robot
Resource          atest_resource.robot

*** Test Cases ***
Test timeout
    ${tc} =    Check Test Case    ${TESTNAME}
    Should Be True    ${tc.elapsed_time.total_seconds()} < 1

Keyword timeout
    ${tc} =    Check Test Case    ${TESTNAME}
    Should Be True    ${tc.elapsed_time.total_seconds()} < 1

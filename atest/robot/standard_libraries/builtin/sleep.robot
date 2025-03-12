*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    standard_libraries/builtin/sleep.robot
Resource          atest_resource.robot

*** Test Cases ***
Sleep
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc[1, 0]}    Slept 1 second 111 milliseconds.
    Check Log Message    ${tc[3, 0]}    Slept 1 second 234 milliseconds.
    Check Log Message    ${tc[5, 0]}    Slept 1 second 112 milliseconds.

Sleep With Negative Time
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc[1, 0]}    Slept 0 seconds.
    Check Log Message    ${tc[2, 0]}    Slept 0 seconds.

Sleep With Reason
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc[0, 0]}    Slept 42 milliseconds.
    Check Log Message    ${tc[0, 1]}    No good reason

Invalid Time Does Not Cause Uncatchable Error
    Check Test Case    ${TESTNAME}

Can Stop Sleep With Timeout
    ${tc}=    Check Test Case    ${TESTNAME}
    Elapsed Time Should Be Valid    ${tc.elapsed_time}    maximum=10

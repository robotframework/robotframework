*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    standard_libraries/builtin/sleep.robot
Resource          atest_resource.robot

*** Test Cases ***
Sleep
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc.kws[1].msgs[0]}    Slept 1 second 111 milliseconds.
    Check Log Message    ${tc.kws[3].msgs[0]}    Slept 1 second 234 milliseconds.
    Check Log Message    ${tc.kws[5].msgs[0]}    Slept 1 second 112 milliseconds.

Sleep With Negative Time
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc.kws[1].msgs[0]}    Slept 0 seconds.
    Check Log Message    ${tc.kws[2].msgs[0]}    Slept 0 seconds.

Sleep With Reason
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc.kws[0].msgs[0]}    Slept 42 milliseconds.
    Check Log Message    ${tc.kws[0].msgs[1]}    No good reason

Invalid Time Does Not Cause Uncatchable Error
    Check Test Case    ${TESTNAME}

Can Stop Sleep With Timeout
    ${tc}=    Check Test Case    ${TESTNAME}
    Elapsed Time Should Be Valid    ${tc.elapsed_time}    maximum=10

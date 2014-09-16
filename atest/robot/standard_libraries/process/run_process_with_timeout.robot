*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    standard_libraries/process/run_process_with_timeout.robot
Force Tags       regression    pybot    jybot
Test Setup       Check Precondition
Resource         process_resource.robot

*** Test Cases ***
Finish before timeout
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc.kws[0].msgs[1]}    Waiting for process to complete.
    Check Log Message    ${tc.kws[0].msgs[2]}    Process completed.

On timeout process is terminated by default
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc.kws[0].msgs[1]}    Waiting for process to complete.
    Check Log Message    ${tc.kws[0].msgs[2]}    Process did not complete in 3 milliseconds.
    Check Log Message    ${tc.kws[0].msgs[3]}    Gracefully terminating process.

On timeout process can be killed
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc.kws[0].msgs[1]}    Waiting for process to complete.
    Check Log Message    ${tc.kws[0].msgs[2]}    Process did not complete in 2 milliseconds.
    Check Log Message    ${tc.kws[0].msgs[3]}    Forcefully killing process.

On timeout process can be left running
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc.kws[0].msgs[1]}    Waiting for process to complete.
    Check Log Message    ${tc.kws[0].msgs[2]}    Process did not complete in 1 millisecond.
    Check Log Message    ${tc.kws[0].msgs[3]}    Leaving process intact.

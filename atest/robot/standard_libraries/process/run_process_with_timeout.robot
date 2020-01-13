*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    standard_libraries/process/run_process_with_timeout.robot
Resource         atest_resource.robot

*** Test Cases ***
Finish before timeout
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc.kws[0].msgs[1]}    Waiting for process to complete.
    Check Log Message    ${tc.kws[0].msgs[2]}    Process completed.

Disable timeout with nONe
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc.kws[0].msgs[1]}    Waiting for process to complete.
    Check Log Message    ${tc.kws[0].msgs[2]}    Process completed.

Disable timeout with empty string
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc.kws[0].msgs[1]}    Waiting for process to complete.
    Check Log Message    ${tc.kws[0].msgs[2]}    Process completed.

Disable timeout with zero
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc.kws[0].msgs[1]}    Waiting for process to complete.
    Check Log Message    ${tc.kws[0].msgs[2]}    Process completed.

Disable timeout with negative value
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc.kws[0].msgs[1]}    Waiting for process to complete.
    Check Log Message    ${tc.kws[0].msgs[2]}    Process completed.

On timeout process is terminated by default (w/ default streams)
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc.kws[0].msgs[1]}    Waiting for process to complete.
    Check Log Message    ${tc.kws[0].msgs[2]}    Process did not complete in 200 milliseconds.
    Check Log Message    ${tc.kws[0].msgs[3]}    Gracefully terminating process.

On timeout process is terminated by default (w/ custom streams)
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc.kws[0].msgs[1]}    Waiting for process to complete.
    Check Log Message    ${tc.kws[0].msgs[2]}    Process did not complete in 200 milliseconds.
    Check Log Message    ${tc.kws[0].msgs[3]}    Gracefully terminating process.

On timeout process can be killed (w/ default streams)
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc.kws[0].msgs[1]}    Waiting for process to complete.
    Check Log Message    ${tc.kws[0].msgs[2]}    Process did not complete in 200 milliseconds.
    Check Log Message    ${tc.kws[0].msgs[3]}    Forcefully killing process.

On timeout process can be killed (w/ custom streams)
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc.kws[0].msgs[1]}    Waiting for process to complete.
    Check Log Message    ${tc.kws[0].msgs[2]}    Process did not complete in 200 milliseconds.
    Check Log Message    ${tc.kws[0].msgs[3]}    Forcefully killing process.
On timeout process can be left running
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc.kws[0].msgs[1]}    Waiting for process to complete.
    Check Log Message    ${tc.kws[0].msgs[2]}    Process did not complete in 200 milliseconds.
    Check Log Message    ${tc.kws[0].msgs[3]}    Leaving process intact.

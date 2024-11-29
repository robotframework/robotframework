*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    standard_libraries/process/wait_for_process.robot
Resource         atest_resource.robot

*** Test Cases ***
Wait For Process
    ${tc} =   Check Test Case    ${TESTNAME}
    Check Log Message    ${tc[1, 0]}    Waiting for process to complete.
    Check Log Message    ${tc[1, 1]}    Process completed.

Wait For Process Timeout
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc[2, 0]}    Waiting for process to complete.
    Check Log Message    ${tc[2, 1]}    Process did not complete in 1 second.
    Check Log Message    ${tc[2, 2]}    Leaving process intact.

Wait For Process Terminate On Timeout
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc[2, 0]}    Waiting for process to complete.
    Check Log Message    ${tc[2, 1]}    Process did not complete in 1 second.
    Check Log Message    ${tc[2, 2]}    Gracefully terminating process.
    Check Log Message    ${tc[2, 3]}    Process completed.

Wait For Process Kill On Timeout
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc[2, 0]}    Waiting for process to complete.
    Check Log Message    ${tc[2, 1]}    Process did not complete in 1 second.
    Check Log Message    ${tc[2, 2]}    Forcefully killing process.
    Check Log Message    ${tc[2, 3]}    Process completed.

Wait for process uses minimum of timeout or internal timeout for polling
    Check Test Case    ${TESTNAME}

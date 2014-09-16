*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    standard_libraries/process/terminate_process.robot
Test Setup       Check Precondition
Force Tags       regression    pybot    jybot
Resource         process_resource.robot

*** Test Cases ***
Terminate process
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc.kws[1].msgs[0]}    Gracefully terminating process.

Kill process
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc.kws[1].msgs[0]}    Forcefully killing process.

Terminate process running on shell
    Check Test Case    ${TESTNAME}

Kill process running on shell
    Check Test Case    ${TESTNAME}

Also child processes are terminated
    Check Test Case    ${TESTNAME}

Also child processes are killed
    Check Test Case    ${TESTNAME}

Kill process when terminate fails
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc.kws[6].msgs[0]}    Gracefully terminating process.
    Check Log Message    ${tc.kws[6].msgs[1]}    Graceful termination failed.
    Check Log Message    ${tc.kws[6].msgs[2]}    Forcefully killing process.
    Should Be True    ${tc.elapsedtime} >= 2000

Terminating already terminated process is ok
    Check Test Case    ${TESTNAME}

Waiting for terminated process is ok
    Check Test Case    ${TESTNAME}

Terminate all processes
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message   ${tc.kws[14].msgs[0]}    Gracefully terminating process.

Terminating all empties cache
    Check Test Case    ${TESTNAME}

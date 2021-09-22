*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    standard_libraries/process/sending_signal.robot
Force Tags       no-windows
Resource         atest_resource.robot

*** Test Cases ***
Sending INT signal
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc.kws[0].kws[1].msgs[0]}    Sending signal INT (2).

Sending SIGINT signal
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc.kws[0].kws[1].msgs[0]}    Sending signal SIGINT (2).

Sending INT signal as a text number
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc.kws[0].kws[1].msgs[0]}    Sending signal 2 (2).

Sending INT signal as a number
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc.kws[0].kws[1].msgs[0]}    Sending signal 2 (2).

Send other well-known signals
    Check Test Case    ${TESTNAME}

By default signal is not sent to process running in shell
    [Tags]    no-osx
    Check Test Case    ${TESTNAME}

By default signal is sent only to parent process
    Check Test Case    ${TESTNAME}

Signal can be sent to process running in shell
    Check Test Case    ${TESTNAME}

Signal can be sent to child processes
    Check Test Case    ${TESTNAME}

Sending an unknown signal
    Check Test Case    ${TESTNAME}

Sending signal to a process with a handle
    Check Test Case    ${TESTNAME}

Sending signal to a process with a wrong handle
    Check Test Case    ${TESTNAME}

*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    standard_libraries/process/stdout_and_stderr.robot
Resource         atest_resource.robot

*** Test Cases ***
Default stdout and stderr
    Check Test Case    ${TESTNAME}

Custom stdout
    Check Test Case    ${TESTNAME}

Redirecting stdout to DEVNULL
    Check Test Case    ${TESTNAME}

Custom stderr
    Check Test Case    ${TESTNAME}

Custom stdout and stderr
    Check Test Case    ${TESTNAME}

Custom stdout and stderr to same file
    Check Test Case    ${TESTNAME}

Redirecting stderr to stdout
    Check Test Case    ${TESTNAME}

Redirecting stderr to custom stdout
    Check Test Case    ${TESTNAME}

Redirecting stderr to DEVNULL
    Check Test Case    ${TESTNAME}

Redirecting stdout and stderr to DEVNULL
    Check Test Case    ${TESTNAME}

Redirecting stdout to DEVNULL and stderr to STDOUT
    Check Test Case    ${TESTNAME}

Custom streams are written under cwd when relative
    Check Test Case    ${TESTNAME}

Cwd does not affect absolute custom streams
    Check Test Case    ${TESTNAME}

Lot of output to custom stream
    Check Test Case    ${TESTNAME}

Lot of output to DEVNULL
    Check Test Case    ${TESTNAME}

Run multiple times
    Check Test Case    ${TESTNAME}

Run multiple times using custom streams
    Check Test Case    ${TESTNAME}

Read standard streams when they are already closed externally
    Check Test Case    ${TESTNAME}

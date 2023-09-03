*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    standard_libraries/process/stdin.robot
Resource          atest_resource.robot

*** Test Cases ***
Stdin is NONE by default
    Check Test Case    ${TESTNAME}

Stdin can be set to PIPE
    Check Test Case    ${TESTNAME}

Stdin can be disabled explicitly
    Check Test Case    ${TESTNAME}

Stdin can be disabled with None object
    Check Test Case    ${TESTNAME}

Stdin as path
    Check Test Case    ${TESTNAME}

Stdin as `pathlib.Path`
    Check Test Case    ${TESTNAME}

Stdin as text
    Check Test Case    ${TESTNAME}

Stdin as stdout from other process
    Check Test Case    ${TESTNAME}

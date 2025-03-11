*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    standard_libraries/operating_system/run.robot
Resource          atest_resource.robot

*** Test Cases ***
Run
    Check Test Case    ${TESTNAME}

Run With RC And Stdout Checks
    Check Test Case    ${TESTNAME}

Run With RC Checks
    Check Test Case    ${TESTNAME}

Run With Stdout Checks
    Check Test Case    ${TESTNAME}

Run With Stderr
    Check Test Case    ${TESTNAME}

Run With Stderr Redirected To Stdout
    Check Test Case    ${TESTNAME}

Run With Stderr Redirected To File
    Check Test Case    ${TESTNAME}

Run When Command Writes Lot Of Stdout And Stderr
    Check Test Case    ${TESTNAME}

Run And Return RC
    Check Test Case    ${TESTNAME}

Run And Return RC And Output
    Check Test Case    ${TESTNAME}

Run Non-ascii Command Returning Non-ascii Output
    Check Test Case    ${TESTNAME}

Trailing Newline Is Removed Automatically
    Check Test Case    ${TESTNAME}

It Is Possible To Start Background Processes
    Check Test Case    ${TESTNAME}

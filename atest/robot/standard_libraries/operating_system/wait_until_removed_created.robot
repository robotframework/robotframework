*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    standard_libraries/operating_system/wait_until_removed_created.robot
Resource          atest_resource.robot

*** Test Cases ***
File And Dir Already Removed
    Check Test Case    ${TESTNAME}

File And Dir Removed Before Timeout
    Check Test Case    ${TESTNAME}

File And Dir Removed With Pattern
    Check Test Case    ${TESTNAME}

File Not Removed Before Timeout
    Check Test Case    ${TESTNAME}

Dir Not Removed Before Timeout
    Check Test Case    ${TESTNAME}

Not Removed Before Timeout With Pattern
    Check Test Case    ${TESTNAME}

Invalid Remove Timeout
    Check Test Case    ${TESTNAME}

File And Dir Already Created
    Check Test Case    ${TESTNAME}

File And Dir Created Before Timeout
    Check Test Case    ${TESTNAME}

File And Dir Created With Pattern
    Check Test Case    ${TESTNAME}

File Not Created Before Timeout
    Check Test Case    ${TESTNAME}

Dir Not Created Before Timeout
    Check Test Case    ${TESTNAME}

Not Created Before Timeout With Pattern
    Check Test Case    ${TESTNAME}

Invalid Create Timeout
    Check Test Case    ${TESTNAME}

Wait Until File With Glob Like Name
    Check Test Case    ${TESTNAME}

Wait Until Removed File With Glob Like Name
    Check Test Case    ${TESTNAME}

Path as `pathlib.Path`
    Check Test Case    ${TESTNAME}

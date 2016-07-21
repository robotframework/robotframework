*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    standard_libraries/process/newlines.robot
Resource         atest_resource.robot

*** Test Cases ***
Trailing newline is removed
    Check Test Case    ${TESTNAME}

Internal newlines are preserved
    Check Test Case    ${TESTNAME}

Newlines with custom stream
    Check Test Case    ${TESTNAME}

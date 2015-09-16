*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    standard_libraries/process/newlines_and_encoding.robot
Resource         atest_resource.robot

*** Test Cases ***
Non-ASCII command and output
    Check Test Case    ${TESTNAME}

Non-ASCII command and output with custom stream
    Check Test Case    ${TESTNAME}

Non-ASCII in environment variables
    Check Test Case    ${TESTNAME}

Trailing newline is removed
    Check Test Case    ${TESTNAME}

Internal newlines are preserved
    Check Test Case    ${TESTNAME}

Newlines with custom stream
    Check Test Case    ${TESTNAME}

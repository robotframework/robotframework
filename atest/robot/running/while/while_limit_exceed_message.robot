*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    running/while/while_limit_exceed_message.robot
Resource          while.resource

*** Test Cases ***
limit_exceed_message without limit
    Check Test Case    ${TESTNAME}

Testing error message
    Check Test Case    ${TESTNAME}

Wrong third argument
    Check Test Case    ${TESTNAME}

Limit exceed message from variable
    Check Test Case    ${TESTNAME}

Part of limit exceed message from variable
    Check Test Case    ${TESTNAME}

No error message
    Check Test Case    ${TESTNAME}

Nested while error message
    Check Test Case    ${TESTNAME}

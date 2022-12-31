*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    running/while/on_limit_message.robot
Resource          while.resource

*** Test Cases ***
Limit exceed message without limit
    Check Test Case    ${TESTNAME}

Wrong third argument
    Check Test Case    ${TESTNAME}

Limit exceed message
    Check Test Case    ${TESTNAME}

Limit exceed message from variable
    Check Test Case    ${TESTNAME}

Part of limit exceed message from variable
    Check Test Case    ${TESTNAME}

No limit exceed message
    Check Test Case    ${TESTNAME}

Nested while limit exceed message
    Check Test Case    ${TESTNAME}

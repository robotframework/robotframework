*** Settings ***
Resource          while.resource
Suite Setup       Run Tests    ${EMPTY}    running/while/invalid_while.robot

*** Test Cases ***
No condition
    Check Test Case    ${TESTNAME}

Multiple conditions
    ${tc} =    Check Test Case    ${TESTNAME}
    Should Be Equal    ${tc.body[0].condition}    Too

Invalid condition
    Check Test Case    ${TESTNAME}

Non-existing variable in condition
    Check Test Case    ${TESTNAME}

No body
    Check Test Case    ${TESTNAME}

No END
    Check Test Case    ${TESTNAME}

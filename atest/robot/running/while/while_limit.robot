*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    running/while/while_limit.robot
Resource          while.resource

*** Test Cases ***
Default limit is 10000 iterations
    Check Test Case    ${TESTNAME}

Limit with iteration count
    Check while loop     FAIL    5

Iteration count with 'times' suffix
    Check while loop     FAIL    3

Iteration count with 'x' suffix
    Check while loop     FAIL    4

Iteration count normalization
    ${tc}=   Check Test Case    ${TESTNAME}
    Should Be Equal    ${tc.body[0].limit}    1_000
    Should Be Equal    ${tc.body[1].limit}    3 0 T i m e S

Limit as timestr
    Check Test Case    ${TESTNAME}

Limit from variable
    Check Test Case    ${TESTNAME}

Part of limit from variable
    Check Test Case    ${TESTNAME}

Limit can be disabled
    Check Test Case    ${TESTNAME}

No Condition With Limit
    Check Test Case    ${TESTNAME}

Limit exceeds in teardown
    Check Test Case    ${TESTNAME}

Limit exceeds after failures in teardown
    Check Test Case    ${TESTNAME}

Continue after limit in teardown
    Check Test Case    ${TESTNAME}

Invalid limit invalid suffix
    Check Test Case    ${TESTNAME}

Invalid limit invalid value
    Check Test Case    ${TESTNAME}

Invalid limit mistyped prefix
    Check Test Case    ${TESTNAME}

Limit used multiple times
    ${tc} =    Check Test Case    ${TESTNAME}
    Should Be Equal    ${tc.body[0].limit}    2

Invalid values after limit
    ${tc} =    Check Test Case    ${TESTNAME}
    Should Be Equal    ${tc.body[0].condition}    $variable < 2, limit=2, invalid

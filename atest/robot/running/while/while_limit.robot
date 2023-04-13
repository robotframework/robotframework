*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    running/while/while_limit.robot
Resource          while.resource

*** Test Cases ***
Default limit is 10000 iterations
    Check Test Case    ${TESTNAME}

Limit with iteration count
    Check while loop     FAIL    5

Limit with iteration count with spaces
    ${tc}=   Check Test Case    ${TESTNAME}
    Should Be Equal    ${tc.body[0].limit}    3 0

Limit with iteration count with underscore
    ${tc}=   Check Test Case    ${TESTNAME}
    Should Be Equal    ${tc.body[0].limit}    1_0

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

Invalid limit invalid suffix
    Check Test Case    ${TESTNAME}

Invalid limit invalid value
    Check Test Case    ${TESTNAME}

Invalid limit mistyped prefix
    Check Test Case    ${TESTNAME}

Invalid values after limit
    ${tc} =    Check Test Case    ${TESTNAME}
    Should Be Equal    ${tc.body[0].condition}    $variable < 2, limit=-1x, invalid, values

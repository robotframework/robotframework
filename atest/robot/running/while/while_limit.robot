*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    running/while/while_limit.robot
Resource          while.resource

*** Test Cases ***
Default limit is 100 iterations
    Check Test Case    ${TESTNAME}

Limit with x iterations
    Check while loop     FAIL    5

Limit with times iterations
    ${tc}=   Check Test Case    ${TESTNAME}
    Should Be Equal    ${tc.body[0].limit}    3 times

Limit as timestr
    Check Test Case    ${TESTNAME}

Limit from variable
    Check Test Case    ${TESTNAME}

Part of limit from variable
    Check Test Case    ${TESTNAME}

Limit can be disabled
    Check Test Case    ${TESTNAME}

Invalid limit no suffix
    Check Test Case    ${TESTNAME}

Invalid limit invalid value
    Check Test Case    ${TESTNAME}

Invalid negative limit
    Check Test Case    ${TESTNAME}

Invalid limit mistyped prefix
    Check Test Case    ${TESTNAME}

Invalid values after limit
    ${tc} =    Check Test Case    ${TESTNAME}
    Should Be Equal    ${tc.body[0].condition}    $variable < 2, limit=-1x, invalid, values

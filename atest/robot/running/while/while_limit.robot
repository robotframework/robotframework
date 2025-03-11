*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    running/while/while_limit.robot
Resource          while.resource

*** Test Cases ***
Default limit is 10000 iterations
    Check WHILE Loop     FAIL    10000

Limit with iteration count
    Check WHILE Loop     FAIL    5

Iteration count with 'times' suffix
    Check WHILE Loop     FAIL    3

Iteration count with 'x' suffix
    Check WHILE Loop     FAIL    4

Iteration count normalization
    ${loop}=   Check WHILE Loop    PASS    1    body[0]
    Should Be Equal    ${loop.limit}    1_000
    ${loop}=   Check WHILE Loop    FAIL    30    body[1]
    Should Be Equal    ${loop.limit}    3 0 T i m e S

Limit as timestr
    Check WHILE Loop    FAIL    not known

Limit from variable
    Check WHILE Loop    FAIL    11

Part of limit from variable
    Check WHILE Loop    FAIL    not known

Limit can be disabled
    Check WHILE Loop    PASS    10041

No condition with limit
    Check WHILE Loop    FAIL    2

Limit exceeds in teardown
    Check WHILE Loop    FAIL    not known    teardown.body[0]

Limit exceeds after failures in teardown
    Check WHILE Loop    FAIL    2            teardown.body[0]

Continue after limit in teardown
    Check WHILE Loop    PASS    not known    teardown.body[0]

Invalid limit invalid suffix
    Check WHILE Loop    FAIL    1    not_run=True

Invalid limit invalid value
    Check WHILE Loop    FAIL    1    not_run=True

Invalid limit mistyped prefix
    Check WHILE Loop    FAIL    1    not_run=True

Limit with non-existing variable
    Check WHILE Loop    FAIL    1    not_run=True

Limit used multiple times
    ${loop}=    Check WHILE Loop    FAIL    1    not_run=True
    Should Be Equal    ${loop.limit}    2

Invalid values after limit
    ${loop}=    Check WHILE Loop    FAIL    1    not_run=True
    Should Be Equal    ${loop.condition}    $variable < 2, limit=2, invalid

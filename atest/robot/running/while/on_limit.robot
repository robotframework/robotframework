*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    running/while/on_limit.robot
Resource          while.resource

*** Test Cases ***
On limit pass with time limit defined
    Check WHILE Loop    PASS    not known

On limit pass with iteration limit defined
    Check WHILE loop    PASS    5

On limit fail
    Check WHILE Loop    FAIL    5

On limit pass with failures in loop
    Check WHILE Loop    FAIL    1

On limit pass with continuable failure
    Check WHILE Loop    FAIL    2

On limit fail with continuable failure
    Check WHILE Loop    FAIL    2

Invalid on_limit
    Check WHILE Loop    FAIL    1    not_run=True

Invalid on_limit from variable
    Check WHILE Loop    FAIL    1    not_run=True

On limit without limit
    Check WHILE Loop    FAIL    1    not_run=True

On limit with invalid variable
    Check WHILE Loop    FAIL    1    not_run=True

On limit message
    Check WHILE Loop    FAIL    11

On limit message without limit
    Check WHILE Loop    FAIL    10000

On limit message from variable
    Check WHILE Loop    FAIL    5

Part of on limit message from variable
    Check WHILE Loop    FAIL    5

On limit message is not used if limit is not hit
    Check WHILE Loop    PASS    2

Nested while on limit message
    Check WHILE Loop    FAIL    1    path=body[0]
    Check WHILE Loop    FAIL    5    path=body[0].body[0].body[0]

On limit message before limit
    Check WHILE Loop    FAIL    5

On limit message with invalid variable
    Check WHILE Loop    FAIL    1    not_run=True

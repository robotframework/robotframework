*** Settings ***
Resource          while.resource
Suite Setup       Run Tests    ${EMPTY}    running/while/break_and_continue.robot

*** Test Cases ***
With CONTINUE
    Check While Loop    PASS    5

With CONTINUE inside IF
    Check While Loop    FAIL    3

With CONTINUE inside TRY
    Check While Loop    PASS    5

With CONTINUE inside EXCEPT and TRY-ELSE
    Check While Loop    PASS    5

With BREAK
    Check While Loop    PASS    1

With BREAK inside IF
    Check While Loop    PASS    2

With BREAK inside TRY
    Check While Loop    PASS    1

With BREAK inside EXCEPT
    Check While Loop    PASS    1

With BREAK inside TRY-ELSE
    Check While Loop    PASS    1

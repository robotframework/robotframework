*** Settings ***
Resource          while.resource
Suite Setup       Run Tests    ${EMPTY}    running/while/break_and_continue.robot
Test Template     Check WHILE loop

*** Test Cases ***
With CONTINUE
    PASS    5

With CONTINUE inside IF
    FAIL    3

With CONTINUE inside TRY
    PASS    5

With CONTINUE inside EXCEPT and TRY-ELSE
    PASS    5

With BREAK
    PASS    1

With BREAK inside IF
    PASS    2

With BREAK inside TRY
    PASS    1

With BREAK inside EXCEPT
    PASS    1

With BREAK inside TRY-ELSE
    PASS    1

BREAK with continuable failures
    FAIL    1

CONTINUE with continuable failures
    FAIL    2

Invalid BREAK
    FAIL    1

Invalid CONTINUE
    FAIL    1

Invalid BREAK not executed
    PASS    1

Invalid CONTINUE not executed
    NOT RUN    1

With CONTINUE in UK
    PASS    5    body[0].body[0]

With CONTINUE inside IF in UK
    FAIL    3    body[0].body[0]

With CONTINUE inside TRY in UK
    PASS    5    body[0].body[0]

With CONTINUE inside EXCEPT and TRY-ELSE in UK
    PASS    5    body[0].body[0]

With BREAK in UK
    PASS    1    body[0].body[0]

With BREAK inside IF in UK
    PASS    2    body[0].body[0]

With BREAK inside TRY in UK
    PASS    1    body[0].body[0]

With BREAK inside EXCEPT in UK
    PASS    1    body[0].body[0]

With BREAK inside TRY-ELSE in UK
    PASS    1    body[0].body[0]

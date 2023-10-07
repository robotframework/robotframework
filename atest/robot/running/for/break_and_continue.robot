*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    running/for/break_and_continue.robot
Resource          for.resource
Test Template     Test and all keywords should have passed

*** Test Cases ***
CONTINUE
    allow not run=True

CONTINUE inside IF
    allow not run=True    allowed failure=Oh no, got 4

CONTINUE inside TRY
    allow not run=True

CONTINUE inside EXCEPT and TRY-ELSE
    allow not run=True    allowed failure=4 == 4

BREAK
    allow not run=True

BREAK inside IF
    allow not run=True

BREAK inside TRY
    allow not run=True

BREAK inside EXCEPT
    allow not run=True    allowed failure=This is excepted!

BREAK inside TRY-ELSE
    allow not run=True

CONTINUE in UK
    allow not run=True

CONTINUE inside IF in UK
    allow not run=True    allowed failure=Oh no, got 4

CONTINUE inside TRY in UK
    allow not run=True

CONTINUE inside EXCEPT and TRY-ELSE in UK
    allow not run=True    allowed failure=4 == 4

BREAK in UK
    allow not run=True

BREAK inside IF in UK
    allow not run=True

BREAK inside TRY in UK
    allow not run=True

BREAK inside EXCEPT in UK
    allow not run=True    allowed failure=This is excepted!

BREAK inside TRY-ELSE in UK
    allow not run=True

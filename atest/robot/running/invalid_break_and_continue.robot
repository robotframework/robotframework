*** Settings ***
Suite setup        Run tests    ${EMPTY}     running/invalid_break_and_continue.robot
Test template      Check test case
Resource           atest_resource.robot

*** Test cases ***
CONTINUE in test case
    ${TEST NAME}

CONTINUE in keyword
    ${TEST NAME}

CONTINUE in IF
    ${TEST NAME}

CONTINUE in ELSE
    ${TEST NAME}

CONTINUE in TRY
    ${TEST NAME}

CONTINUE in EXCEPT
    ${TEST NAME}

CONTINUE in TRY-ELSE
    ${TEST NAME}

CONTINUE with argument in FOR
    ${TEST NAME}

CONTINUE with argument in WHILE
    ${TEST NAME}

BREAK in test case
    ${TEST NAME}

BREAK in keyword
    ${TEST NAME}

BREAK in IF
    ${TEST NAME}

BREAK in ELSE
    ${TEST NAME}

BREAK in TRY
    ${TEST NAME}

BREAK in EXCEPT
    ${TEST NAME}

BREAK in TRY-ELSE
    ${TEST NAME}

BREAK with argument in FOR
    ${TEST NAME}

BREAK with argument in WHILE
    ${TEST NAME}

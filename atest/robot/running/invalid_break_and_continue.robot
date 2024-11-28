*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    running/invalid_break_and_continue.robot
Resource          atest_resource.robot

*** Test Cases ***
CONTINUE in test case
    Check Test Case    ${TESTNAME}

CONTINUE in keyword
    Check Test Case    ${TESTNAME}

CONTINUE in IF
    Check Test Case    ${TESTNAME}

CONTINUE in ELSE
    Check Test Case    ${TESTNAME}

CONTINUE in TRY
    Check Test Case    ${TESTNAME}

CONTINUE in EXCEPT
    Check Test Case    ${TESTNAME}

CONTINUE in TRY-ELSE
    Check Test Case    ${TESTNAME}

CONTINUE with argument in FOR
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc[0, 0, 1, 0]}   CONTINUE does not accept arguments, got 'should not work'.    FAIL

CONTINUE with argument in WHILE
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc[0, 0, 1, 0]}   CONTINUE does not accept arguments, got 'should', 'not' and 'work'.    FAIL

BREAK in test case
    Check Test Case    ${TESTNAME}

BREAK in keyword
    Check Test Case    ${TESTNAME}

BREAK in IF
    Check Test Case    ${TESTNAME}

BREAK in ELSE
    Check Test Case    ${TESTNAME}

BREAK in TRY
    Check Test Case    ${TESTNAME}

BREAK in EXCEPT
    Check Test Case    ${TESTNAME}

BREAK in TRY-ELSE
    Check Test Case    ${TESTNAME}

BREAK with argument in FOR
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc[0, 0, 1, 0]}   BREAK does not accept arguments, got 'should not work'.    FAIL

BREAK with argument in WHILE
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc[0, 0, 1, 0]}   BREAK does not accept arguments, got 'should', 'not' and 'work'.    FAIL

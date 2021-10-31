*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    running/if/invalid_inline_if.robot
Test Template     Check IF/ELSE Status
Resource          if.resource

*** Test Cases ***
Invalid condition
    FAIL    NOT RUN

Invalid condition with other error
    FAIL    NOT RUN

Empty IF
    FAIL

IF without branch
    FAIL

IF without branch with ELSE IF
    FAIL    NOT RUN    else=False

IF without branch with ELSE
    FAIL    NOT RUN

IF followed by ELSE IF
    FAIL

IF followed by ELSE
    FAIL

Empty ELSE IF
    FAIL       NOT RUN    test=${TESTNAME} 1    else=False
    NOT RUN    FAIL       test=${TESTNAME} 2    else=False

ELSE IF without branch
    FAIL    NOT RUN               test=${TESTNAME} 1    else=False
    FAIL    NOT RUN    NOT RUN    test=${TESTNAME} 2

Empty ELSE
    FAIL    NOT RUN    NOT RUN

ELSE IF after ELSE
    FAIL    NOT RUN    NOT RUN               types=['IF', 'ELSE', 'ELSE IF']               test=${TESTNAME} 1
    FAIL    NOT RUN    NOT RUN    NOT RUN    types=['IF', 'ELSE', 'ELSE IF', 'ELSE IF']    test=${TESTNAME} 2

Multiple ELSEs
    FAIL    NOT RUN    NOT RUN               types=['IF', 'ELSE', 'ELSE']            test=${TESTNAME} 1
    FAIL    NOT RUN    NOT RUN    NOT RUN    types=['IF', 'ELSE', 'ELSE', 'ELSE']    test=${TESTNAME} 2

Nested IF
    FAIL               test=${TESTNAME} 1
    FAIL    NOT RUN    test=${TESTNAME} 2
    FAIL               test=${TESTNAME} 3

Nested FOR
    FAIL

Unnecessary END
    PASS       NOT RUN    index=0
    NOT RUN    FAIL       index=1

Assign in IF branch
    FAIL

Assign in ELSE IF branch
    FAIL    NOT RUN    else=False

Assign in ELSE branch
    FAIL    NOT RUN

Invalid assign mark usage
    FAIL

Too many list variables in assign
    FAIL    NOT RUN

Invalid number of variables in assign
    NOT RUN    FAIL

Invalid value for list assign
    FAIL

Invalid value for dict assign
    NOT RUN    FAIL

Assign when IF branch is empty
    FAIL

Assign when ELSE IF branch is empty
    FAIL    NOT RUN    else=False

Assign when ELSE branch is empty
    FAIL    NOT RUN

Assign with RETURN
    [Template]    NONE
    ${tc} =    Check Test Case    ${TESTNAME}
    Check IF/ELSE Status    FAIL    NOT RUN    root=${tc.body[0].body[0]}

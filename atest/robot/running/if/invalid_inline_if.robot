*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    running/if/invalid_inline_if.robot
Test Template     Check IF/ELSE Status
Resource          if.resource

*** Test Cases ***
Invalid condition
    FAIL    NOT RUN

Condition with non-existing variable
    FAIL

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

Invalid END after inline header
    [Template]    NONE
    ${tc} =    Check Test Case    ${TEST NAME}
    Check IF/ELSE Status    PASS    root=${tc.body[0]}
    Check Log Message     ${tc.body[0].body[0].body[0].body[0]}   Executed inside inline IF
    Check Log Message     ${tc.body[1].body[0]}                   Executed outside IF
    Should Be Equal       ${tc.body[2].type}                      ERROR
    Should Be Equal       ${tc.body[2].status}                    FAIL

Assign in IF branch
    FAIL

Assign in ELSE IF branch
    FAIL    NOT RUN    else=False

Assign in ELSE branch
    FAIL    NOT RUN

Invalid assign mark usage
    FAIL    NOT RUN

Too many list variables in assign
    FAIL    NOT RUN

Invalid number of variables in assign
    NOT RUN    FAIL

Invalid value for list assign
    FAIL    NOT RUN

Invalid value for dict assign
    NOT RUN    FAIL

Assign when IF branch is empty
    FAIL    NOT RUN

Assign when ELSE IF branch is empty
    FAIL    NOT RUN    NOT RUN

Assign when ELSE branch is empty
    FAIL    NOT RUN

Control structures are allowed
    [Template]    NONE
    ${tc} =    Check Test Case    ${TESTNAME}
    Check IF/ELSE Status    NOT RUN    PASS    root=${tc.body[0].body[0]}

Control structures are not allowed with assignment
    [Template]    NONE
    ${tc} =    Check Test Case    ${TESTNAME}
    Check IF/ELSE Status    FAIL    NOT RUN    root=${tc.body[0].body[0]}

*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    running/if/inline_if_else.robot
Test Template     Check IF/ELSE Status
Resource          if.resource

*** Test Cases ***
IF passing
    PASS    else=False

IF failing
    FAIL    else=False

Not executed
    NOT RUN    else=False

Not executed after failure
    NOT RUN    NOT RUN    NOT RUN    index=1    run=False

ELSE IF not executed
    NOT RUN    NOT RUN    PASS       index=0
    FAIL       NOT RUN    NOT RUN    index=1    else=False

ELSE IF executed
    NOT RUN    PASS       NOT RUN                          index=0
    NOT RUN    NOT RUN    FAIL       NOT RUN    NOT RUN    index=1

ELSE not executed
    PASS       NOT RUN    index=0
    FAIL       NOT RUN    index=1

ELSE executed
    NOT RUN    PASS       index=0
    NOT RUN    FAIL       index=1

Assign
    PASS       NOT RUN    NOT RUN    index=0
    NOT RUN    PASS       NOT RUN    index=1
    NOT RUN    NOT RUN    PASS       index=2

Multi assign
    PASS       NOT RUN

List assign
    PASS       NOT RUN    index=0
    NOT RUN    PASS       index=2

Dict assign
    NOT RUN    PASS

Inside FOR
    [Template]    NONE
    ${tc} =    Check Test Case    ${TEST NAME}
    Check IF/ELSE Status    NOT RUN    PASS       root=${tc.body[0].body[0].body[0]}
    Check IF/ELSE Status    NOT RUN    PASS       root=${tc.body[0].body[1].body[0]}
    Check IF/ELSE Status    FAIL       NOT RUN    root=${tc.body[0].body[2].body[0]}

Inside normal IF
    [Template]    NONE
    ${tc} =    Check Test Case    ${TEST NAME}
    Check IF/ELSE Status    NOT RUN    PASS       root=${tc.body[0].body[0].body[1]}
    Check IF/ELSE Status    NOT RUN    NOT RUN    root=${tc.body[0].body[1].body[0]}    run=False

In keyword
    [Template]    NONE
    ${tc} =    Check Test Case    ${TEST NAME}
    Check IF/ELSE Status    PASS                                     root=${tc.body[0].body[0]}
    Check IF/ELSE Status    NOT RUN    PASS       NOT RUN            root=${tc.body[0].body[1]}
    Check IF/ELSE Status    NOT RUN    NOT RUN    NOT RUN    FAIL
    ...                     NOT RUN    NOT RUN    NOT RUN            root=${tc.body[0].body[2]}

Invalid END after inline header
    # FIXME: Move to separate suite with other invalid syntax tests
    [Template]    NONE
    Check Test Case    ${TEST NAME}

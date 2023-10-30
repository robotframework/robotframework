*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    running/if/inline_if_else.robot
Test Template     Check IF/ELSE Status
Resource          if.resource

*** Test Cases ***
IF passing
    PASS

IF failing
    FAIL

IF erroring
    FAIL

Not executed
    NOT RUN

Not executed after failure
    NOT RUN    NOT RUN    NOT RUN    index=1    run=False

Not executed after failure with assignment
    [Template]    NONE
    ${tc} =    Check Test Case    ${TEST NAME}
    Check IF/ELSE Status    NOT RUN    NOT RUN    root=${tc.body[1]}    run=False
    Check IF/ELSE Status    NOT RUN    NOT RUN    root=${tc.body[2]}    run=False
    Check Keyword Data      ${tc.body[1].body[0].body[0]}    Not run    assign=\${x}           status=NOT RUN
    Check Keyword Data      ${tc.body[2].body[0].body[0]}    Not run    assign=\${x}, \@{y}    status=NOT RUN

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

Assign with item
    PASS       NOT RUN    NOT RUN    index=0
    NOT RUN    PASS       NOT RUN    index=1
    NOT RUN    NOT RUN    PASS       index=2

Multi assign
    PASS       NOT RUN    index=0
    FAIL       NOT RUN    index=4

List assign
    PASS       NOT RUN    index=0
    NOT RUN    PASS       index=2

Dict assign
    NOT RUN    PASS

Assign based on another variable
    PASS       NOT RUN    index=1

Assign without ELSE
    PASS       NOT RUN               index=0
    NOT RUN    PASS       NOT RUN    index=2

Assign when no branch is run
    NOT RUN    PASS                  index=0
    NOT RUN    NOT RUN    PASS       index=2
    NOT RUN    PASS                  index=4

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
    Check IF/ELSE Status    PASS       NOT RUN                       root=${tc.body[0].body[0]}
    Check IF/ELSE Status    NOT RUN    PASS       NOT RUN            root=${tc.body[0].body[1]}
    Check IF/ELSE Status    NOT RUN    NOT RUN    NOT RUN    FAIL
    ...                     NOT RUN    NOT RUN    NOT RUN            root=${tc.body[0].body[2]}

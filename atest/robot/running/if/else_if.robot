*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    running/if/else_if.robot
Test Template     Check IF/ELSE Status
Resource          if.resource

*** Test Cases ***
Else if condition 1 passes
    PASS    NOT RUN    NOT RUN

Else if condition 2 passes
    NOT RUN    PASS    NOT RUN

Else if else passes
    NOT RUN    NOT RUN    PASS

Else if condition 1 failing
    FAIL    NOT RUN    NOT RUN

Else if condition 2 failing
    NOT RUN    FAIL    NOT RUN

Else if else failing
    NOT RUN    NOT RUN    FAIL

Invalid
    FAIL    NOT RUN

After failure
    NOT RUN    NOT RUN    NOT RUN    index=1    run=False

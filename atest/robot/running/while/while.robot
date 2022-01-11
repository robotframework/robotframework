*** Settings ***
Resource          while.resource
Suite Setup       Run Tests    ${EMPTY}    running/while/while.robot

*** Test Cases ***
Loop executed once
    ${loop}=    Check While Loop    PASS    1
    Check Log Message   ${loop.body[0].body[0].msgs[0]}    1

Loop executed multiple times
    Check While Loop    PASS    5

Loop not executed
    Check While Loop    NOT RUN    1

Execution fails on the first loop
    Check While Loop    FAIL    1

Execution fails after some loops
    Check While Loop    FAIL    3

In keyword
    ${tc}=    Check test case    ${TEST NAME}
    Check loop attributes    ${tc.body[0].body[0]}    PASS    3

Loop fails in keyword
    ${tc}=    Check test case    ${TEST NAME}
    Check loop attributes    ${tc.body[0].body[0]}    FAIL    2

With RETURN
    ${tc}=    Check test case    ${TEST NAME}
    Check loop attributes    ${tc.body[0].body[0]}    PASS    1

With Continue For Loop
    Check While Loop    FAIL    3

With Exit For Loop
    Check While Loop    PASS    2

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
    ${loop} =    Check While Loop    NOT RUN    1
    Length Should Be    ${loop.body[0].body}    2
    FOR    ${item}    IN    ${loop.body[0]}    @{loop.body[0].body}
        Should Be Equal    ${item.status}    NOT RUN
    END

Execution fails on the first loop
    Check While Loop    FAIL    1

Execution fails after some loops
    Check While Loop    FAIL    3

In keyword
    Check While Loop    PASS    3    path=body[0].body[0]

Loop fails in keyword
    Check While Loop    FAIL    2    path=body[0].body[0]

With RETURN
    Check While Loop    PASS    1    path=body[0].body[0]

With Continue For Loop
    Check While Loop    FAIL    3

With Exit For Loop
    Check While Loop    PASS    2

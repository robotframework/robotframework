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

No Condition
    Check While Loop    PASS    5

Execution fails on the first loop
    Check While Loop    FAIL    1

Execution fails after some loops
    Check While Loop    FAIL    3

Continuable failure in loop
    Check While Loop    FAIL    3

Normal failure after continuable failure in loop
    Check While Loop    FAIL    2

Normal failure outside loop after continuable failures in loop
    Check While Loop    FAIL    2

Loop in loop
    Check While Loop    PASS    5
    Check While Loop    PASS    3    path=body[0].body[0].body[2]

In keyword
    Check While Loop    PASS    3    path=body[0].body[0]

Loop fails in keyword
    Check While Loop    FAIL    2    path=body[0].body[0]

With RETURN
    Check While Loop    PASS    1    path=body[0].body[0]

Condition evaluation time is included in elapsed time
    ${loop} =    Check WHILE loop    PASS    1
    Elapsed Time Should Be Valid    ${loop.elapsed_time}            minimum=0.2
    Elapsed Time Should Be Valid    ${loop.body[0].elapsed_time}    minimum=0.1

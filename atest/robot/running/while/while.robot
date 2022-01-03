*** Settings ***
Resource          while_resource.robot
Suite Setup       Run Tests    ${EMPTY}    running/while/while.robot

*** Test Cases ***
While loop executed once
    ${loop}=    Check While Loop    PASS    1
    Check Log Message   ${loop.body[0].body[0].msgs[0]}    1

While loop executed multiple times
    Check While Loop    PASS    5

While loop not executed
    Check While Loop    NOT RUN    1

While loop execution fails on the first loop
    Check While Loop    FAIL    1

While loop execution fails after some loops
    Check While Loop    FAIL    3

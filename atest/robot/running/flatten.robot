*** Settings ***
Suite Setup       Run Tests    --loglevel trace --listener flatten_listener.Listener    running/flatten.robot
Resource          atest_resource.robot

*** Test Cases ***
A single user keyword
    ${tc}=    User keyword content should be flattened    1
    Check Log Message    ${tc[0, 0]}    From the main kw

Nested UK
    ${tc}=    User keyword content should be flattened    2
    Check Log Message    ${tc[0, 0]}    arg
    Check Log Message    ${tc[0, 1]}    from nested kw

Loops and stuff
    ${tc}=    User keyword content should be flattened     13
    Check Log Message    ${tc[0, 0]}     inside for 0
    Check Log Message    ${tc[0, 1]}     inside for 1
    Check Log Message    ${tc[0, 2]}     inside for 2
    Check Log Message    ${tc[0, 3]}     inside while 0
    Check Log Message    ${tc[0, 4]}     \${LIMIT} = 1
    Check Log Message    ${tc[0, 5]}     inside while 1
    Check Log Message    ${tc[0, 6]}     \${LIMIT} = 2
    Check Log Message    ${tc[0, 7]}     inside while 2
    Check Log Message    ${tc[0, 8]}     \${LIMIT} = 3
    Check Log Message    ${tc[0, 9]}     inside if
    Check Log Message    ${tc[0, 10]}    fail inside try    FAIL
    Check Log Message    ${tc[0, 11]}    Traceback (most recent call last):*    DEBUG    pattern=True
    Check Log Message    ${tc[0, 12]}    inside except

Recursion
    User keyword content should be flattened     8

Listener methods start and end keyword are called
    Stderr Should Be Empty

Log levels
    Run Tests    ${EMPTY}    running/flatten.robot
    ${tc}=    User keyword content should be flattened    4
    Check Log Message    ${tc[0, 0]}     INFO 1
    Check Log Message    ${tc[0, 1]}     Log level changed from INFO to DEBUG.    DEBUG
    Check Log Message    ${tc[0, 2]}     INFO 2
    Check Log Message    ${tc[0, 3]}     DEBUG 2    level=DEBUG

*** Keywords ***
User keyword content should be flattened
    [Arguments]    ${expected_message_count}=0
    ${tc}=   Check Test Case    ${TESTNAME}
    Length Should Be    ${tc[0].body}        ${expected_message_count}
    Length Should Be    ${tc[0].messages}    ${expected_message_count}
    RETURN    ${tc}

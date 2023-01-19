*** Settings ***
Suite Setup       Run Tests    --loglevel trace --listener flatten_listener.Listener    running/flatten.robot
Resource          atest_resource.robot

*** Test Cases ***
A single user keyword
    ${tc}=    User keyword content should be flattened    1
    Check Log Message    ${tc.body[0].messages[0]}    From the main kw

Nested UK
    ${tc}=    User keyword content should be flattened    2
    Check Log Message    ${tc.body[0].messages[0]}    arg
    Check Log Message    ${tc.body[0].messages[1]}    from nested kw

Loops and stuff
    ${tc}=    User keyword content should be flattened     19
    Check Log Message    ${tc.body[0].messages[0]}     inside for 0
    Check Log Message    ${tc.body[0].messages[5]}     inside while 0
    Check Log Message    ${tc.body[0].messages[15]}     inside if
    Check Log Message    ${tc.body[0].messages[18]}     inside except

Recursion
    User keyword content should be flattened     8

Listener methods start and end keyword are called
    Stderr Should Be Empty

*** Keywords ***
User keyword content should be flattened
    [Arguments]    ${expected_message_count}=0
    ${tc}=   Check Test Case    ${TESTNAME}
    ${kw}=   set variable    ${tc.body[0]}
    Length Should Be    ${kw.body}    ${expected_message_count}
    Length Should Be   ${kw.messages}    ${expected_message_count}
    RETURN    ${tc}

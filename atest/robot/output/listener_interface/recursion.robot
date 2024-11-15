*** Settings ***
Suite Setup       Run Tests    --listener ${LISTENER DIR}/Recursion.py    ${LISTENER DIR}/recursion.robot
Resource          listener_resource.robot

*** Test Cases ***
Recursion in start_keyword, end_keyword and log_message
    ${tc} =               Check Test Case                  Test
    Length Should Be      ${tc.body}                       1
    VAR                   ${kw}                            ${tc.body[0]}
    Check Keyword Data    ${kw}                            BuiltIn.Log    args=3                       children=5
    Check Keyword Data    ${kw.body[0]}                    BuiltIn.Log    args=2 (by start_keyword)    children=4
    Check Keyword Data    ${kw.body[0].body[0]}            BuiltIn.Log    args=1 (by start_keyword)    children=1
    Check Log Message     ${kw.body[0].body[0].body[0]}    1 (by start_keyword)
    Check Log Message     ${kw.body[0].body[1]}            1 (by log_message)
    Check Log Message     ${kw.body[0].body[2]}            2 (by start_keyword)
    Check Keyword Data    ${kw.body[0].body[3]}            BuiltIn.Log    args=1 (by end_keyword)      children=1
    Check Log Message     ${kw.body[0].body[3].body[0]}    1 (by end_keyword)
    Check Log Message     ${kw.body[1]}                    1 (by log_message)
    Check Log Message     ${kw.body[2]}                    2 (by log_message)
    Check Log Message     ${kw.body[3]}                    3
    Check Keyword Data    ${kw.body[4]}                    BuiltIn.Log    args=2 (by end_keyword)      children=4
    Check Keyword Data    ${kw.body[4].body[0]}            BuiltIn.Log    args=1 (by start_keyword)    children=1
    Check Log Message     ${kw.body[4].body[0].body[0]}    1 (by start_keyword)
    Check Log Message     ${kw.body[4].body[1]}            1 (by log_message)
    Check Log Message     ${kw.body[4].body[2]}            2 (by end_keyword)
    Check Keyword Data    ${kw.body[4].body[3]}            BuiltIn.Log    args=1 (by end_keyword)      children=1
    Check Log Message     ${kw.body[4].body[3].body[0]}    1 (by end_keyword)

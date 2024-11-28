*** Settings ***
Suite Setup       Run Tests    --listener ${LISTENER DIR}/Recursion.py    ${LISTENER DIR}/recursion.robot
Resource          listener_resource.robot

*** Test Cases ***
Limited recursion in start_keyword, end_keyword and log_message
    ${tc} =               Check Test Case                  Limited recursion
    Length Should Be      ${tc.body}                       1
    VAR                   ${kw}                            ${tc[0]}
    Check Keyword Data    ${kw}             BuiltIn.Log    args=Limited 3                       children=5
    Check Keyword Data    ${kw[0]}          BuiltIn.Log    args=Limited 2 (by start_keyword)    children=4
    Check Keyword Data    ${kw[0, 0]}       BuiltIn.Log    args=Limited 1 (by start_keyword)    children=1
    Check Log Message     ${kw[0, 0, 0]}    Limited 1 (by start_keyword)
    Check Log Message     ${kw[0, 1]}       Limited 1 (by log_message)
    Check Log Message     ${kw[0, 2]}       Limited 2 (by start_keyword)
    Check Keyword Data    ${kw[0, 3]}       BuiltIn.Log    args=Limited 1 (by end_keyword)      children=1
    Check Log Message     ${kw[0, 3, 0]}    Limited 1 (by end_keyword)
    Check Log Message     ${kw[1]}          Limited 1 (by log_message)
    Check Log Message     ${kw[2]}          Limited 2 (by log_message)
    Check Log Message     ${kw[3]}          Limited 3
    Check Keyword Data    ${kw[4]}          BuiltIn.Log    args=Limited 2 (by end_keyword)      children=4
    Check Keyword Data    ${kw[4, 0]}       BuiltIn.Log    args=Limited 1 (by start_keyword)    children=1
    Check Log Message     ${kw[4, 0, 0]}    Limited 1 (by start_keyword)
    Check Log Message     ${kw[4, 1]}       Limited 1 (by log_message)
    Check Log Message     ${kw[4, 2]}       Limited 2 (by end_keyword)
    Check Keyword Data    ${kw[4, 3]}       BuiltIn.Log    args=Limited 1 (by end_keyword)      children=1
    Check Log Message     ${kw[4, 3, 0]}    Limited 1 (by end_keyword)

Unlimited recursion in start_keyword, end_keyword and log_message
    Check Test Case       Unlimited recursion
    Check Recursion Error    ${ERRORS[0]}    start_keyword    Recursive execution stopped.
    Check Recursion Error    ${ERRORS[1]}    end_keyword      Recursive execution stopped.
    Check Recursion Error    ${ERRORS[2]}    log_message      RecursionError: *

*** Keywords ***
Check Recursion Error
    [Arguments]    ${msg}    ${method}    ${error}
    ${listener} =    Normalize Path    ${LISTENER DIR}/Recursion.py
    Check Log Message    ${msg}
    ...    Calling method '${method}' of listener '${listener}' failed: ${error}
    ...    ERROR    pattern=True

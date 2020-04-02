*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    running/timeouts_with_custom_messages.robot
Resource          atest_resource.robot

*** Test Cases ***
Default Test Timeout Message
    Check Test Case    ${TEST NAME}
    Using more than one value with timeout should error    0    2     2    Test Timeout

Test Timeout Message
    Check Test Case    ${TEST NAME}
    Using more than one value with timeout should error    1    9     2

Test Timeout Message In Multiple Columns
    Check Test Case    ${TEST NAME}
    Using more than one value with timeout should error    2    13    7

Keyword Timeout Message
    Check Test Case    ${TEST NAME}
    Using more than one value with timeout should error    3    26    2

Keyword Timeout Message In Multiple Columns
    Check Test Case    ${TEST NAME}
    Using more than one value with timeout should error    4    30    7

*** Keywords ***
Using more than one value with timeout should error
    [Arguments]    ${index}    ${lineno}    ${count}    ${setting}=Timeout
    Error In File
    ...    ${index}    running/timeouts_with_custom_messages.robot    ${lineno}
    ...    Setting '${setting}' accepts only one value, got ${count}.

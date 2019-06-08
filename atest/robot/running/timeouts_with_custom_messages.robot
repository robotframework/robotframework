*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    running/timeouts_with_custom_messages.robot
Resource          atest_resource.robot

*** Test Cases ***
Default Test Timeout Message
    Check Test Case    ${TEST NAME}
    Using more than one value with timeout should error    0    2    Test Timeout

Test Timeout Message
    Check Test Case    ${TEST NAME}
    Using more than one value with timeout should error    1    2

Test Timeout Message In Multiple Columns
    Check Test Case    ${TEST NAME}
    Using more than one value with timeout should error    2    7

Keyword Timeout Message
    Check Test Case    ${TEST NAME}
    Using more than one value with timeout should error    3    2

Keyword Timeout Message In Multiple Columns
    Check Test Case    ${TEST NAME}
    Using more than one value with timeout should error    4    7

*** Keywords ***
Using more than one value with timeout should error
    [Arguments]    ${index}    ${count}    ${setting}=Timeout
    ${path} =    Normalize Path    ${DATADIR}/running/timeouts_with_custom_messages.robot
    ${error} =    Catenate    Error in file '${path}':
    ...    Setting '${setting}' accepts only one value, got ${count}.
    Check Log Message    ${ERRORS}[${index}]    ${error}    ERROR

*** Settings ***
Suite Setup       Run Tests    --exclude exclude    running/duplicate_test_name.robot
Resource          atest_resource.robot

*** Test Cases ***
Tests with same name should be executed
    Should Contain Tests    ${SUITE}
    ...    Same Test Multiple Times
    ...    Same Test Multiple Times
    ...    Same Test Multiple Times
    ...    Same Test With Different Case And Spaces
    ...    SameTestwith Different CASE and s p a c e s
    ...    Same Test In Data But Only One Executed

There should be warning when multiple tests with same name are executed
    Check Multiple Tests Log Message    ${ERRORS[0]}    Same Test Multiple Times
    Check Multiple Tests Log Message    ${ERRORS[1]}    Same Test Multiple Times
    Check Multiple Tests Log Message    ${ERRORS[2]}    SameTestwith Different CASE and s p a c e s

There should be no warning when there are multiple tests with same name in data but only one is executed
    ${tc} =    Check Test Case    Same Test In Data But Only One Executed
    Check Log Message    ${tc.kws[0].msgs[0]}    This is executed!
    Length Should Be    ${ERRORS}    3

*** Keywords ***
Check Multiple Tests Log Message
    [Arguments]    ${error}    ${test}
    Check Log Message
    ...    ${error}
    ...    Multiple tests with name '${test}' executed in suite 'Duplicate Test Name'.
    ...    WARN

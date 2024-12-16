*** Settings ***
Suite Setup       Run Tests    --exclude exclude    running/duplicate_test_name.robot
Resource          atest_resource.robot

*** Test Cases ***
Tests with same name are executed
    Should Contain Tests    ${SUITE}
    ...    Duplicates
    ...    Duplicates
    ...    Duplicates
    ...    Duplicates with different case and spaces
    ...    Duplicates with different CASE ands p a c e s
    ...    Duplicates but only one executed
    ...    Test 1    Test 2    Test 3
    ...    Duplicates after resolving variables
    ...    Duplicates after resolving variables

There is warning when multiple tests with same name are executed
    Check Multiple Tests Log Message    ${ERRORS[0]}    Duplicates
    Check Multiple Tests Log Message    ${ERRORS[1]}    Duplicates
    Check Multiple Tests Log Message    ${ERRORS[2]}    Duplicates with different CASE ands p a c e s

There is warning if names are same after resolving variables
    Check Multiple Tests Log Message    ${ERRORS[3]}    Duplicates after resolving variables

There is no warning when there are multiple tests with same name but only one is executed
    Check Test Case    Duplicates but only one executed
    Length Should Be    ${ERRORS}    4

Original name can be same if there is variable and its value changes
    Check Test Case    Test 1
    Check Test Case    Test 2
    Check Test Case    Test 3
    Length Should Be    ${ERRORS}    4

*** Keywords ***
Check Multiple Tests Log Message
    [Arguments]    ${error}    ${test}
    Check Log Message
    ...    ${error}
    ...    Multiple tests with name '${test}' executed in suite 'Duplicate Test Name'.
    ...    WARN

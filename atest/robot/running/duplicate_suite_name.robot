*** Settings ***
Suite Setup       Run Tests    --exclude exclude    running/duplicate_suite_name
Resource          atest_resource.robot

*** Test Cases ***
Suites with same name shoul be executed
    Should Contain Suites    ${SUITE}
    ...    Test
    ...    Test

There should be warning when multiple suites with aame name are executed
    Check Multiple Suites Log Message    ${ERRORS[0]}    Test

There should be no warning if suites with same name are run explicitly
    ${sources} =    Catenate
    ...    running/duplicate_suite_name/test.robot
    ...    running/duplicate_suite_name/test_.robot
    ...    running/duplicate_suite_name/test.robot
    Run Tests    ${EMPTY}    ${sources}
    Should Contain Suites    ${SUITE}
    ...    Test
    ...    Test
    ...    Test
    Should Be Empty    ${ERRORS}

*** Keywords ***
Check Multiple Suites Log Message
    [Arguments]    ${error}    ${name}
    Check Log Message
    ...    ${error}
    ...    Multiple suites with name '${name}' executed in suite 'Duplicate Suite Name'.
    ...    WARN

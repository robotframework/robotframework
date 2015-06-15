*** Settings ***
Suite Setup        Warning in    suite setup
Suite Teardown     Warning in    suite teardown
Non-Existing       Causes error

*** Test Cases ***
Warning in test case
    Warning in    test case

Warning in test case
    [Documentation]    Duplicate name causes warning
    No warning

Error in test case
    Error in test case

*** Keywords ***
Warning in
    [Arguments]    ${where}
    [Tags]    warn
    Log    Warning in ${where}    WARN

No warning
    [Tags]    warn
    Log    No warnings here

Error in test case
    [Tags]    warn    error
    Log    Logged errors supported since 2.9    ERROR

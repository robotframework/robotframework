*** Settings ***
Suite Setup        Warning in    suite setup
Suite Teardown     Warning in    suite teardown
Non-Existing       Causes error

*** Test cases ***
Warning in test case
    Warning in    test case

Warning in test case
    [Documentation]    Duplicate name causes warning
    Log    No warnings here

*** Keywords ***
Warning in
    [Arguments]    ${where}
    Log    Warning in ${where}    WARN

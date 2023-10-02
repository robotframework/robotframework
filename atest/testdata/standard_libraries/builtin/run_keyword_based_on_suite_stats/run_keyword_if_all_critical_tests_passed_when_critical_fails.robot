*** Settings ***
Suite Teardown    Run Keyword If All Critical Tests Passed    Fail    ${NON EXISTING}    #Should not be executed nor evaluated
Default Tags      critical

*** Test Cases ***
Run Keyword If All Critical Tests Passed Is not executed when Critcal Test Fails
    [Documentation]    FAIL Expected failure
    Fail    Expected failure

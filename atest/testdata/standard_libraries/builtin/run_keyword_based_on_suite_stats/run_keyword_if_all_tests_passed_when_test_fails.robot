*** Settings ***
Suite Teardown    Run Keyword If All Tests Passed    Fail    ${NON EXISTING}    #Should not be executed nor evaluated

*** Test Cases ***
Run Keyword If All tests Passed Is not Executed When Any Test Fails
    [Documentation]    FAIL Expected failure
    Fail    Expected failure

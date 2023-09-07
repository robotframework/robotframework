*** Test Cases ***
Run Keyword If All Critical Tests Passed Can't be Used In Test
    [Documentation]    FAIL Keyword 'Run Keyword If All Critical Tests Passed' can only be used in suite teardown.
    Run Keyword If All Critical Tests Passed    Fail    ${NON EXISTING}    #Should not be executed nor evaluated

Run Keyword If Any Critical Tests Failed Can't be Used In Test
    [Documentation]    FAIL Keyword 'Run Keyword If Any Critical Tests Failed' can only be used in suite teardown.
    Run Keyword If Any Critical Tests Failed    Fail    ${NON EXISTING}    #Should not be executed nor evaluated

Run Keyword If All Tests Passed Can't be Used In Test
    [Documentation]    FAIL Keyword 'Run Keyword If All Tests Passed' can only be used in suite teardown.
    Run Keyword If All Tests Passed    Fail    ${NON EXISTING}    #Should not be executed nor evaluated

Run Keyword If Any Tests Failed Can't be Used In Test
    [Documentation]    FAIL Keyword 'Run Keyword If Any Tests Failed' can only be used in suite teardown.
    Run Keyword If Any Tests Failed    Fail    ${NON EXISTING}    #Should not be executed nor evaluated

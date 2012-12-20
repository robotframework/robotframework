*** Test Cases ***

Should return True when keyword Succeeds
    ${actual}=    Run keyword and return status    Should Be Equal    a    a
    Should Be Equal    ${TRUE}    ${actual}

Should return False when keyword Fails
    ${actual}=    Run keyword and return status    Should Be Equal    a    b
    Should Be Equal    ${FALSE}    ${actual}

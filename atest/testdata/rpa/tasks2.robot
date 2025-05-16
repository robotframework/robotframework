*** Variables ***
${RPA}           True

*** Tasks ***
Passing
    Should Be Equal    ${OPTIONS.rpa}    ${RPA}    type=bool

Failing
    [Documentation]    FAIL Error
    Fail    Error

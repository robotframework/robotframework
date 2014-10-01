*** Test Cases ***
Using keyword defined twice fails
    [Documentation]    FAIL Keyword 'Defined Twice' defined multiple times.
    Defined twice

Using keyword defined thrice fails as well
    [Documentation]    FAIL Keyword 'DEFINED THRICE' defined multiple times.
    Defined thrice

*** Keywords ***
Defined twice
    Fail    This is not executed

Defined Twice
    Fail    This is not executed either

Defined thrice
    Fail    This is not executed

Defined Thrice
    Fail    This is not executed either

DEFINED THRICE
    Fail    Neither is this

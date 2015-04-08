*** Test Cases ***
Using keyword defined twice fails
    [Documentation]    FAIL Keyword with same name defined multiple times.
    Defined twice

Using keyword defined thrice fails as well
    [Documentation]    FAIL Keyword with same name defined multiple times.
    Defined thrice

Keyword with embedded arguments defined twice: Cannot be called with embedded args
    [Documentation]    FAIL No keyword with name 'Embedded arguments twice' found.
    Embedded arguments twice

Keyword with embedded arguments defined twice: Can be called with exact name
    [Documentation]    FAIL Keyword with same name defined multiple times.
    Embedded ${arguments match} twice

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

Embedded ${arguments} twice
    Fail    This is not executed

Embedded ${arguments match} TWICE
    Fail    This is not executed

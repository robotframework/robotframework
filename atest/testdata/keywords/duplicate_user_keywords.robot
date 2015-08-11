*** Variables ***
${INDENT}         ${SPACE * 4}

*** Test Cases ***
Using keyword defined twice fails
    [Documentation]    FAIL Keyword with same name defined multiple times.
    Defined twice

Using keyword defined thrice fails as well
    [Documentation]    FAIL Keyword with same name defined multiple times.
    Defined thrice

Keyword with embedded arguments defined twice fails at run-time: Called with embedded args
    [Documentation]    FAIL
    ...    Test case file contains multiple keywords matching name 'Embedded arguments twice':
    ...    ${INDENT}Embedded \${arguments match} TWICE
    ...    ${INDENT}Embedded \${arguments} twice
    Embedded arguments twice

Keyword with embedded arguments defined twice fails at run-time: Called with exact name
    [Documentation]    FAIL
    ...    Test case file contains multiple keywords matching name 'Embedded ${arguments match} twice':
    ...    ${INDENT}Embedded \${arguments match} TWICE
    ...    ${INDENT}Embedded \${arguments} twice
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

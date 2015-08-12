*** Settings ***
Library          DupeKeywords.py

*** Variables ***
${INDENT}         ${SPACE * 4}

*** Test Cases ***
Using keyword defined twice fails
    [Documentation]    FAIL Keyword with same name defined multiple times.
    Defined TWICE

Using keyword defined thrice fails as well
    [Documentation]    FAIL Keyword with same name defined multiple times.
    Defined thrice

Keyword with embedded arguments defined twice fails at run-time: Called with embedded args
    [Documentation]    FAIL
    ...    Test library 'DupeKeywords' contains multiple keywords matching name 'Embedded arguments twice':
    ...    ${INDENT}Embedded \${arguments match} TWICE
    ...    ${INDENT}Embedded \${arguments} twice
    Embedded arguments twice

Keyword with embedded arguments defined twice fails at run-time: Called with exact name
    [Documentation]    FAIL
    ...    Test library 'DupeKeywords' contains multiple keywords matching name 'Embedded ${arguments match} twice':
    ...    ${INDENT}Embedded \${arguments match} TWICE
    ...    ${INDENT}Embedded \${arguments} twice
    Embedded ${arguments match} twice

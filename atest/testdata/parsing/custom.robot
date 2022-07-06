*** H 1 ***
S 1                Suite documentation.
S 2                Metadata    Value
S 3                Suite Setup
S 4                Suite Teardown
S 5                Test Setup
S 6                Test Teardown
S 7                Test Template
S 8                1 minute
S 9                test    tags
S 10               keyword    tags
L                  OperatingSystem
R                  custom.resource
V                  variables.py

*** H 2 ***
${VARIABLE}        variable value

*** H 3 ***
Test without settings
    Nothing to see here

Test with settings
    [S 1]              Test documentation.
    [S 14]             own tag
    [S 11]             NONE
    [S 12]             NONE
    [S 13]             NONE
    [S 15]             NONE
    Keyword            ${VARIABLE}

*** H 5 ***
Suite Setup
    Directory Should Exist    ${CURDIR}

Suite Teardown
    Keyword In Resource

Test Setup
    Should Be Equal    ${VARIABLE}         variable value
    Should Be Equal    ${RESOURCE FILE}    variable in resource file
    Should Be Equal    ${VARIABLE FILE}    variable in variable file

Test Teardown
    No Operation

Test Template
    [S 16]    ${message}
    Log    ${message}

Keyword
    [S 1]     Keyword documentation.
    [S 16]    ${arg}
    [S 14]    own tag
    [S 15]    1h
    Should Be Equal    ${arg}    ${VARIABLE}
    [S 12]    No Operation

*** H 6 ***
Ignored comments.

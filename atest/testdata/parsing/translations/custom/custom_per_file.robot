language: custom
*** H S ***
N                  Custom name
D                  Suite documentation.
M                  Metadata    Value
S S                Suite Setup
S T                Suite Teardown
T S                Test Setup
T Tea              Test Teardown
t tem              Test Template
T ti               1 minute
t Ta               test    tags
k T                keyword    tags
L                  OperatingSystem
R                  resource.resource
V                  ../../variables.py

*** h v ***
${VARIABLE}        variable value

*** H TE ***
Test without settings
    Nothing to see here

Test with settings
    [D]            Test documentation.
    [Ta]           own tag
    [S]            NONE
    [tea]          NONE
    [tEm]          NONE
    [ti]           NONE
    Keyword        ${VARIABLE}

*** h K ***
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
    [A]    ${message}
    Log    ${message}

Keyword
    [d]      Keyword documentation.
    [a]      ${arg}
    [ta]     own tag
    [tI]     1h
    [S]      Log    Hello, setup!
    Should Be Equal    ${arg}    ${VARIABLE}
    [TEA]    No Operation

*** H C ***
Ignored comments.

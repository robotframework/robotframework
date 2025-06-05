*** Settings ***
Suite Setup       Embedded ${LIST}
Suite Teardown    Embedded ${LIST}

*** Variables ***
@{LIST}           one    ${2}
${NOT}            not, exact match instead

*** Test Cases ***
Test setup and teardown
    [Setup]       Embedded ${LIST}
    No Operation
    [Teardown]    Embedded ${LIST}

Keyword setup and teardown
    Keyword setup and teardown

Exact match after replacing variables has higher precedence
    [Setup]       Embedded ${NOT}
    Exact match after replacing variables has higher precedence
    [Teardown]    Embedded ${NOT}

*** Keywords ***
Keyword setup and teardown
    [Setup]       Embedded ${LIST}
    No Operation
    [Teardown]    Embedded ${LIST}

Embedded ${args}
    Should Be Equal    ${args}    ${LIST}

Embedded not, exact match instead
    No Operation

Exact match after replacing variables has higher precedence
    [Setup]       Embedded ${NOT}
    No Operation
    [Teardown]    Embedded ${NOT}

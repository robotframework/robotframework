*** Settings ***
Suite Setup       Embedded ${LIST}
Suite Teardown    Embedded ${LIST}

*** Variables ***
@{LIST}    one    ${2}

*** Test Cases ***
Test setup and teardown
    [Setup]       Embedded ${LIST}
    No Operation
    [Teardown]    Embedded ${LIST}

Keyword setup and teardown
    Keyword setup and teardown

*** Keywords ***
Keyword setup and teardown
    [Setup]       Embedded ${LIST}
    No Operation
    [Teardown]    Embedded ${LIST}

Embedded ${args}
    Should Be Equal    ${args}    ${LIST}

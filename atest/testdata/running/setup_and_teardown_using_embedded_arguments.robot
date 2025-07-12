*** Settings ***
Suite Setup       Embedded "arg"
Suite Teardown    Object ${LIST}

*** Variables ***
${ARG}            arg
${QUOTED}         "${ARG}"
@{LIST}           one    ${2}
${NOT}            not, exact match instead

*** Test Cases ***
Test setup and teardown
    [Setup]       Embedded "arg"
    No Operation
    [Teardown]    Embedded "arg"

Keyword setup and teardown
    Keyword setup and teardown

Argument as variable
    [Setup]       Embedded "${ARG}"
    Keyword setup and teardown as variable
    [Teardown]    Embedded "${ARG}"

Argument as non-string variable
    [Setup]       Object ${LIST}
    Keyword setup and teardown as non-string variable
    [Teardown]    Object ${LIST}

Argument matching only after replacing variables
    [Setup]       Embedded ${QUOTED}
    Keyword setup and teardown matching only after replacing variables
    [Teardown]    Embedded ${QUOTED}

Exact match after replacing variables has higher precedence
    [Setup]       Embedded ${NOT}
    Exact match after replacing variables has higher precedence
    [Teardown]    Embedded ${NOT}

*** Keywords ***
Embedded "${arg}"
    Should Be Equal    ${arg}    arg

Object ${arg}
    Should Be Equal    ${arg}    ${LIST}

Keyword setup and teardown
    [Setup]       Embedded "arg"
    No Operation
    [Teardown]    Embedded "arg"

Keyword setup and teardown as variable
    [Setup]       Embedded "${ARG}"
    No Operation
    [Teardown]    Embedded "${ARG}"

Keyword setup and teardown as non-string variable
    [Setup]       Object ${LIST}
    No Operation
    [Teardown]    Object ${LIST}

Keyword setup and teardown matching only after replacing variables
    [Setup]       Embedded ${QUOTED}
    No Operation
    [Teardown]    Embedded ${QUOTED}

Embedded not, exact match instead
    No Operation

Exact match after replacing variables has higher precedence
    [Setup]       Embedded ${NOT}
    No Operation
    [Teardown]    Embedded ${NOT}

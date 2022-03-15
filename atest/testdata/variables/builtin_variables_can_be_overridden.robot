*** Settings ***
Resource          override_builtin_variables.resource

*** Variables ***
${TEMPDIR}        Overridden
${42}             fourtytwo

*** Test Cases ***
Overridden from CLI
    Should Be Equal    ${SPACE}        space
    Should Be Equal    ${-1}           negative

Overridden in variables section
    Should Be Equal    ${TEMPDIR}      Overridden
    Should Be Equal    ${42}           fourtytwo

Overridden in resource file
    Should Be Equal    ${NONE}         Someone
    Should Be Equal    ${3.14}         pi

Overridden locally 1
    ${TRUE} =          Set Variable    ${FALSE}
    ${0} =             Set Variable    zero
    ${TEST NAME} =     Set Variable    bad idea
    Should Be Equal    ${TRUE}         ${FALSE}
    Should Be Equal    ${0}            zero
    Should Be Equal    ${TEST NAME}    bad idea

Overridden locally 2
    Should Be Equal    ${TRUE}         ${TRUE}
    Should Be Equal    ${0}            ${{0}}
    Should Be Equal    ${TEST NAME}    Overridden locally 2

*** Settings ***
Library         OperatingSystem

*** Variables ***
${VAR}            var table
@{LIST}           1    2
&{DICT}           a=1    1=b
${EMBEDDED 1}     embedded 1
${EMBEDDED 2}     embedded 2

*** Test Cases ***
Get value when variable exists
    ${x} =    Get Variable Value    ${VAR}
    Should be equal    ${x}    var table
    ${y} =    Get Variable Value    ${x}    default value
    Should be equal    ${y}    var table

Get value when variable doesn't exist
    ${x} =    Get Variable Value    ${nonex}
    Should be equal    ${x}    ${None}
    ${y} =    Get Variable Value    ${nonex}    default value
    Should be equal    ${y}    default value

Get value when default value is none
    ${x} =    Get Variable Value    ${nonex}    none
    Should be equal    ${x}    none

Default value contains variables
    ${x} =    Get Variable Value    ${nonex}    ${VAR}
    Should be equal    ${x}    var table
    ${y} =    Get Variable Value    ${nonex}    <${VAR.replace(' ', '')}>
    Should be equal    ${y}    <vartable>
    ${z} =    Get Variable Value    ${nonex}    ${42}
    Should be equal    ${z}    ${42}

Use escaped variable syntaxes
    ${x} =    Get Variable Value    $VAR
    Should be equal    ${x}    var table
    ${y} =    Get Variable Value    \${VAR}
    Should be equal    ${y}    var table
    ${z} =    Get Variable Value    $NONEX    default
    Should be equal    ${z}    default

List variables
    @{x} =    Get Variable Value    @{LIST}
    Should be true    ${x}    ${LIST}
    @{x} =    Get Variable Value    @{nonex}    @{LIST}
    Should be true    ${x}    ${LIST}
    @{x} =    Get Variable Value    @{nonex}
    Should be empty    ${x}

Extended variable syntax
    ${x} =    Get Variable Value    ${VAR.upper()}
    Should Be Equal    ${x}    VAR TABLE
    ${x} =    Get Variable Value    ${VAR.nonex}    default
    Should Be Equal    ${x}    default
    ${x} =    Get Variable Value    ${LIST[0]}
    Should Be Equal    ${x}    1
    ${x} =    Get Variable Value    ${DICT['a']}
    Should Be Equal    ${x}    1
    ${x} =    Get Variable Value    ${LIST[2]}    default
    Should Be Equal    ${x}    default
    ${x} =    Get Variable Value    ${DICT['c']}    default
    Should Be Equal    ${x}    default

Nested variable
    ${x} =    Get Variable Value    ${EMBEDDED ${1}}
    Should Be Equal    ${x}    embedded 1
    ${x} =    Get Variable Value    ${EMBEDDED ${LIST}[1]}
    Should Be Equal    ${x}    embedded 2
    ${x} =    Get Variable Value    ${EMBEDDED ${LIST}[5]}    default
    Should Be Equal    ${x}    default
    ${x} =    Get Variable Value    ${DICT['${DICT['a']}']}
    Should Be Equal    ${x}    b
    ${x} =    Get Variable Value    ${DICT['${DICT['nonex']}']}    default
    Should Be Equal    ${x}    default

List and dict variable items
    ${x} =    Get Variable Value    ${LIST}[0]
    Should Be Equal    ${x}    1
    ${x} =    Get Variable Value    ${DICT}[a]
    Should Be Equal    ${x}    1
    ${x} =    Get Variable Value    ${LIST}[2]    default
    Should Be Equal    ${x}    default
    ${x} =    Get Variable Value    ${DICT}[c]    default
    Should Be Equal    ${x}    default

Invalid variable syntax 1
    [Documentation]    FAIL Invalid variable name 'notvar'.
    Get Variable Value    notvar

Invalid variable syntax 2
    [Documentation]    FAIL Invalid variable name '\\'.
    Get Variable Value    \

Invalid variable syntax 3
    [Documentation]    FAIL Invalid variable name '\%{X}'.
    Get Variable Value    %{X}

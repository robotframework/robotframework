*** Variables ***
${JOHN HOME}      /home/john
${JANE HOME}      /home/jane
@{PERSONS}        John    Jane
${PERSON}         ${PERSONS}[${${i}-${${${i}}}}]
${PERSON2}        ${${PER}SONS}[${i}]
&{PERSON INFO}    name=${${PER}SONS}[${${i}-${${${i}}}}]
...               ${PER[${i}].lower()}m${${PER}SON${2} [${i}]}il=${${PER}SONS[${${i}-${${${i}}}}].lower()}@${PERSONS[${i}].lower()}.com
${HOME}           ${${PERSON} HOME}
${HOME2}          ${${${PER}SON${2}} HOME}
${X}              x
${X2}             ${${X}}
${X3}             ${${${${ ${${${x}}} ${${${i}}+${i}} }}}}
${i}              1
${per}            PER

*** Test Cases ***
Variable Inside Variable In Variable Table
    Should Be Equal    ${HOME}    /home/john
    Should Be Equal    ${HOME2}    /home/jane
    Should Be Equal    ${X2}    x
    Should Be Equal    ${X3}    x

Variable Inside Variable In Test Case
    ${place} =    Set Variable    home
    Should Be Equal    ${${person${2}} ${place}}    /home/jane
    ${name}    ${my string}    ${method}    ${,} =    Create List    my string    a,b,c    split    ,
    # 'a,b,c' . split (',' , 2)
    ${a}    ${b}    ${c} =    Set Variable    ${ ${name} . ${method} ('${,}' ${,} ${${${i}}+${i}}) }
    Should Be Equal    -${a}-${b}-${c}-    -a-b-c-

Variable Inside Variable In User Keyword
    My UK    john    ${${PER SON} HOME}

Variable Inside List Variables
    ${names} =    Catenate    SEPARATOR=&    @{${PER}SONS}
    ${names} =    Catenate    SEPARATOR=-    @{ ${ P E R } S O N S }    ${names}
    Should Be Equal    ${names}    John-Jane-John&Jane
    Should Be True    @{${PER}SONS} == ['John', 'Jane']
    Should Be Equal    ${${PER} SONS}[0]    John
    Should Be Equal    ${ ${ p e r } s o n s }[${1}]    Jane

Variable Inside Dict Variables
    Should Be Equal    ${${PER}SON INFO.name}    John
    Should Be Equal    ${${PER}SON INFO.email}    john@jane.com

Variable Inside Variable Item
    Should Be Equal    -${PERSON}-${PERSON2}-    -John-Jane-
    Should Be Equal    -${PERSONS}[${${i} - ${i}}]-${PERSONS}[${${${${${i}}}}}]-    -John-Jane-
    Should Be Equal    ${PERSON INFO}[n${ ${PER} SON ${2} [${i}] }me]    John
    Should Be Equal    ${ ${PERSONS}[ ${${i} + ${${${i}}} - ${${i} * 2}} ] HOME.upper() }    /HOME/JOHN
    ${numbers} =    Evaluate    range(10)
    Should Be Equal    ${PERSONS}[${numbers}[${i}]]    Jane

Variable Inside Variable And Extended Variable Syntax
    # This is slightly complicated =)
    Should Be Equal    ${ ${ ${PERSON${3*2-4}} HOME.split('/')[${i}] } [-4:].capitalize() }    John

Non-Existing Variable Inside Variable
    [Documentation]    FAIL Variable '\${nonexisting1}' not found.
    Log    ${whatever ${nonexisting${${i}}}}

*** Keywords ***
My UK
    [Arguments]    ${name}    ${exp home}
    Should Be Equal    ${${name} HOME}    ${exp home}

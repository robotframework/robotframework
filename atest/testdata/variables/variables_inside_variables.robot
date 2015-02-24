*** Variables ***
${i}  1
${JOHN HOME}  /home/john
${JANE HOME}  /home/jane
@{PERSONS}  John  Jane
${PERSON}  @{PERSONS}[${${i}-${${${i}}}}]
${PERSON2}  @{PERSONS}[${i}]
${HOME}  ${${PERSON} HOME}
${HOME2}  ${${PERSON${2}} HOME}
${X}  x
${X2}  ${${X}}
${X3}  ${${${${ ${${${x}}} ${${${i}}+${i}} }}}}

*** Test Cases ***
Variable Inside Variable In Variable Table
    Should Be Equal  ${HOME}  /home/john
    Should Be Equal  ${HOME2}  /home/jane
    Should Be Equal  ${X2}  x
    Should Be Equal  ${X3}  x

Variable Inside Variable In Test Case
    ${place} =  Set Variable  home
    Should Be Equal  ${${person${2}} ${place}}  /home/jane
    ${name}  ${my string}  ${method}  ${,} =  Create List  my string  a,b,c  split
    ...  ,
    ${a}  ${b}  ${c} =  Set Variable  ${ ${name} . ${method} ('${,}' ${,} ${${${i}}+${i}}) }
    Comment  Above is:  'a,b,c' . split (',' , 2)
    Should Be Equal  -${a}-${b}-${c}-  -a-b-c-

Variable Inside Variable In User Keyword
    My UK  john  ${${PER SON} HOME}

Variable Inside List Variable
    ${var} =  Set Variable  PER
    ${names} =  Catenate  SEPARATOR=&  @{${var}SONS}
    ${names} =  Catenate  SEPARATOR=&  @{ ${ v a r } S O N S }  ${names}
    Should Be Equal  ${names}  John&Jane&John&Jane
    Should Be True  @{${var}SONS} == ['John', 'Jane']
    Should Be Equal  @{${VAR} SONS}[0]  John
    Should Be Equal  @{ ${ v a r } s o n s }[${1}]  Jane

Variable Inside List Variable Index
    Should Be Equal  -${PERSON}-${PERSON2}-  -John-Jane-  In variable table
    Should Be Equal  ${ @{PERSONS}[ ${${i}+${${${i}}}-${${i}*2}} ] HOME.upper()}  /HOME/JOHN

Variable Inside Variable And Extended Variable Syntax
    Should Be Equal  ${ ${ ${PERSON${3*2-4}} HOME.split('/')[${i}] } [-4:].capitalize() }  John  This is slightly complicated =)

Non-Existing Variable Inside Variable
    [Documentation]  FAIL Variable '\${nonexisting1}' not found.
    Log  ${whatever ${nonexisting${${i}}}}

*** Keywords ***
My UK
    [Arguments]  ${name}  ${exp home}
    Should Be Equal  ${${name} HOME}  ${exp home}


*** Settings ***
Library           OperatingSystem

*** Variables ***
@{LIST}           Hello    world

*** Test Cases ***
Replace Variables
    ${template} =    Get File    ${CURDIR}${/}template.txt
    Replace Variables And Verify Content    ${template}    Pekka    fine    morning
    Replace Variables And Verify Content    ${template}    Juha    dark    and    gloomy    evening

Replace Variables Using Extended Variable Syntax
    ${what} =    Set Variable    Python
    ${replaced} =    Replace Variables    I like \${WHAT.upper()}! Me ${1 * 2}!!
    Should Be Equal    ${replaced}    I like PYTHON! Me 2!!

Replace Variables Fails When Variable Does Not Exist
    [Documentation]    FAIL Variable '\${non existing variables}' not found.
    Replace Variables    Using \${non existing variables} is an error

Replace Variables With Escaped Variables
    ${result} =    Replace Variables    \\\${non existing} but escaped
    Should Be Equal    ${result}    \${non existing} but escaped
    ${result} =    Replace Variables    \${LIST}[0] \\\${LIST}[1]
    Should Be Equal    ${result}    Hello \${LIST}[1]

Replace Variables With Scalar Object
    ${replaced} =    Replace Variables    \${42}
    Should Be Equal    ${replaced}    ${42}    Should be an integer
    ${replaced} =    Replace Variables    \${42} is the answer
    Should Be Equal    ${replaced}    42 is the answer    Should be a string
    Import Variables    ${CURDIR}/numbers_to_convert.py
    ${replaced} =    Replace Variables    \${OBJECT}
    Should Be Equal    ${replaced}    ${OBJECT}    Should be a custom object
    ${replaced} =    Replace Variables    \${OBJECT.value}
    Should Be Equal    ${replaced}    ${1}    Should be an integer
    ${replaced} =    Replace Variables    \${OBJECT} \${OBJECT.value}
    Should Be Equal    ${replaced}    MyObject 1    Should be a string

Replace Variables With List Variable
    @{replaced} =    Replace Variables    \@{LIST}
    Should Be Equal    ${replaced}[0]    Hello
    Should Be Equal    ${replaced}[1]    world
    @{mixed} =    Create List    ${1}    ${True}    xxx    ${LIST}
    @{replaced} =    Replace Variables    \@{mixed}
    Should Be Equal    ${replaced}[0]    ${1}
    Should Be Equal    ${replaced}[1]    ${True}
    Should Be Equal    ${replaced}[2]    xxx
    Should Be Equal    ${replaced}[3]    ${LIST}

*** Keywords ***
Replace Variables And Verify Content
    [Arguments]    ${template}    ${name}    @{occasion}
    ${replaced} =    Replace Variables    ${template}
    Should Be Equal    ${replaced}    Hello ${name}!\nHow are you on this @{occasion}?\n

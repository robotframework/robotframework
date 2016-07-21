*** Settings ***
Suite Teardown    Remove Base Test Directory
Test Setup        Create Test Directories
Resource          os_resource.robot

*** Variables ***
${DIR}            foodir
${F1}             foo.txt
${F2}             nön-äscïï.txt

*** Test Cases ***
List And Count Directory
    List And Count Directory    ${F1}    ${DIR}    ${F2}
    Remove File    ${BASE}/${F1}
    List And Count Directory    ${DIR}    ${F2}
    Remove File    ${BASE}/${F2}
    List And Count Directory    ${DIR}
    Remove Directory    ${BASE}/${DIR}
    List And Count Directory

List And Count Files In Directory
    List And Count Files In Directory    ${F1}    ${F2}
    Remove Files    ${BASE}/${F1}    ${BASE}/${F2}
    List And Count Files In Directory

List And Count Directories In Directory
    List And Count Directories In Directory    ${DIR}
    Remove Directory    ${BASE}/${DIR}
    List And Count Directories In Directory

List And Count Directory With Patterns
    List And Count Directory With Pattern    *.txt    ${F1}    ${F2}
    List And Count Directory With Pattern    f??*    ${F1}    ${DIR}
    List And Count Directory With Pattern    nomatch

List And Count Files In Directory With Patterns
    List And Count Files In Directory With Pattern    *    ${F1}    ${F2}
    List And Count Files In Directory With Pattern    foo*    ${F1}
    List And Count Files In Directory With Pattern    none

List And Count Directories In Directory With Patterns
    List And Count Directories In Directory With Pattern    f*    ${DIR}
    List And Count Directories In Directory With Pattern    *.txt

List Directory With Absolute
    @{items} =    List Directory    ${BASE}    *.txt    absolute
    Listing Should Have Correct Items    ${items}    ${BASE}${/}${F1}    ${BASE}${/}${F2}
    @{items} =    List Files In Directory    ${BASE}    absolute=yes
    Listing Should Have Correct Items    ${items}    ${BASE}${/}${F1}    ${BASE}${/}${F2}
    @{items} =    List Directories In Directory    ${BASE}    ${EMPTY}    yes
    Listing Should Have Correct Items    ${items}    ${BASE}${/}${DIR}

*** Keywords ***
Create Test Directories
    Remove Base Test Directory
    Create Directory    ${BASE}
    Create Directory    ${BASE}/${DIR}
    Create File    ${BASE}/${F1}
    Create File    ${BASE}/${F2}

List And Count Directory
    [Arguments]    @{expected}
    @{items} =    List Directory    ${BASE}
    ${count} =    Count Items In Directory    ${BASE}
    Lists Should Be Equal    ${items}    ${expected}
    Length Should Be    ${items}    ${count}

List And Count Directory With Pattern
    [Arguments]    ${pattern}    @{expected}
    @{items} =    List Directory    ${BASE}    ${pattern}    absolute=no
    ${count} =    Count Items In Directory    ${BASE}    ${pattern}
    Lists Should Be Equal    ${items}    ${expected}
    Length Should Be    ${items}    ${count}

List And Count Files In Directory
    [Arguments]    @{expected}
    ${items} =    List Files In Directory    ${BASE}
    ${count} =    Count Files In Directory    ${BASE}
    Lists Should Be Equal    ${items}    ${expected}
    Length Should Be    ${items}    ${count}

List And Count Files In Directory With Pattern
    [Arguments]    ${pattern}    @{expected}
    ${items} =    List Files In Directory    ${BASE}    ${pattern}    absolute=${FALSE}
    ${count} =    Count Files In Directory    ${BASE}    ${pattern}
    Lists Should Be Equal    ${items}    ${expected}
    Length Should Be    ${items}    ${count}

List And Count Directories In Directory
    [Arguments]    @{expected}
    ${items} =    List Directories In Directory    ${BASE}
    ${count} =    Count Directories In Directory    ${BASE}
    Lists Should Be Equal    ${items}    ${expected}
    Length Should Be    ${items}    ${count}

List And Count Directories In Directory With Pattern
    [Arguments]    ${pattern}    @{expected}
    ${items} =    List Directories In Directory    ${BASE}    ${pattern}
    ${count} =    Count Directories In Directory    ${BASE}    ${pattern}
    Lists Should Be Equal    ${items}    ${expected}
    Length Should Be    ${items}    ${count}

Listing Should Have Correct Items
    [Arguments]    ${items}    @{expected}
    Lists Should Be Equal    ${items}    ${expected}

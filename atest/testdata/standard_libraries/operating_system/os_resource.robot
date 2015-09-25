*** Settings ***
Library           OperatingSystem
Library           Collections

*** Variables ***
${BASE}           %{TEMPDIR}${/}robot-os-tests
${TESTFILE SHORT NAME}    f1.txt
${TESTFILE}       ${BASE}${/}${TESTFILE SHORT NAME}
${TESTFILE 2 SHORT NAME}    f2.txt
${TESTFILE 2}     ${BASE}${/}${TESTFILE 2 SHORT NAME}
${TESTDIR}        ${BASE}${/}d1
${NON ASCII}      ${BASE}${/}nön-äscïï
${WITH SPACE}     ${BASE}${/}with space

*** Keywords ***
Verify File
    [Arguments]    ${path}    ${expected}    ${encoding}=UTF-8
    ${content} =    Log File    ${path}    ${encoding}
    Should Be Equal    ${content}    ${expected}

Create Base Test Directory
    Remove Base Test Directory
    Create Directory    ${BASE}

Remove Base Test Directory
    Remove Directory    ${BASE}    recursive

Directory Should Have Items
    [Arguments]    ${path}    @{expected}
    ${items} =    List Directory    ${path}
    Lists Should Be Equal    ${items}    ${expected}

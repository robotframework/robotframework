*** Settings ***
Documentation     Tests for different file and directory names.
...               These are, for most parts, tested also elsewhere.
Test Setup        Create Base Test Directory
Suite Teardown    Remove Base Test Directory
Resource          os_resource.robot

*** Test Cases ***
ASCII only file name
    Test File Operations    ascii

File name with spaces
    Test File Operations    ascii only also here

Non-ASCII file name with ordinals < 255
    Test File Operations    nön-äscïi

Non-ASCII file name with ordinals > 255
    Test File Operations    ŋöñ-äßçíï-€

ASCII only directory name
    Test Directory Operations    ascii

Directory name with spaces
    Test Directory Operations    ascii only also here

Non-ASCII directory name with ordinals < 255
    Test Directory Operations    nön-äscïi

Non-ASCII directory name with ordinals > 255
    Test Directory Operations    ŋöñ-äßçíï-€

*** Keywords ***
Test File Operations
    [Arguments]    ${name}
    ${path} =    Join Path    ${BASE}    ${name}
    Should Be Equal    ${path}    ${BASE}${/}${name}
    Test File Creation, Existence, And Getting    ${path}
    Test Copy And Move File    ${path}
    Test Remove File    ${path}

Test File Creation, Existence, And Getting
    [Arguments]    ${path}
    File Should Not Exist    ${path}
    Touch    ${path}
    File Should Exist    ${path}
    File Should Be Empty    ${path}
    Create File    ${path}    ${path}
    File Should Not Be Empty    ${path}
    ${content} =    Get File    ${path}
    Should Be Equal    ${content}    ${path}

Test Copy And Move File
    [Arguments]    ${path}
    Copy File    ${path}    ${path}-new
    File Should Exist    ${path}
    File Should Exist    ${path}-new
    Move File    ${path}-new    ${path}-newer
    File Should Not Exist    ${path}-new
    File Should Exist    ${path}-newer

Test Remove File
    [Arguments]    ${path}
    File Should Exist    ${path}
    Remove File    ${path}
    File Should Not Exist    ${path}
    File Should Exist    ${path}-*
    Remove File    ${path}-*
    File Should Not Exist    ${path}-*

Test Directory Operations
    [Arguments]    ${name}
    ${path} =    Normalize Path    ${BASE}/${name}
    Should Be Equal    ${path}    ${BASE}${/}${name}
    Directory Should Not Exist    ${path}
    Create Directory    ${path}
    Directory Should Exist    ${path}
    Directory Should Be Empty    ${path}
    Create File    ${path}/${name}
    Directory Should Not Be Empty    ${path}
    @{items} =    List Directory    ${path}
    Length Should Be    ${items}    1
    Should Be Equal    ${items}[0]    ${name}
    Remove Directory    ${path}    recursive
    Directory Should Not Exist    ${path}

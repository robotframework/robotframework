*** Settings ***
Test Setup      Create Base Test Directory
Suite Teardown  Remove Base Test Directory
Resource        os_resource.robot

*** Test Cases ***
Create File With Default Content
    Create File    ${TESTFILE}
    Verify File    ${TESTFILE}    ${EMPTY}

Create File With Content
    [Template]    Create and Verify File
    ${EMPTY}
    Content in one line
    This is content in\n3\nlines
    Nön-ÄSCÏÏ Cöntënt

Create Non-ASCII File With Default Encoding
    Create File    ${TESTFILE}    Nön-ÄSCÏÏ Cöntënt
    Verify File    ${TESTFILE}    Nön-ÄSCÏÏ Cöntënt

Create File With Encoding
    [Template]    Create and Verify File
    Just ASCII     ASCII
    Hyvää yötä!    UTF-8
    Hyvää yötä!    ISO-8859-1
    Спасибо        UTF-8
    Спасибо        ISO-8859-5

Create File With Non-ASCII Name
    [Template]    Create and Verify File
    ASCII content    file=${NON ASCII}
    Спасибо          file=${NON ASCII}

Create File With Space In Name
    Create And Verify File    file=${WITH SPACE}

Create File To Non-Existing Directory
    Create And Verify File    file=${TESTDIR}${/}file.txt

Creating File Fails If Encoding Is Incorrect
    [Documentation]    FAIL REGEXP: Unicode(Encode|)Error: .*
    Create File    ${TESTFILE}    Hyvää yötä!    ASCII

Create Binary File Using Bytes
    [Template]    Create And Verify Binary File Using Bytes
    ${EMPTY}
    Hello, world!
    Hyvää yötä!
    \x00\x01\xe4\xff

Create Binary File Using Unicode
    [Template]    Create And Verify Binary File Using Unicode
    ${EMPTY}
    Hello, world!
    Hyvää yötä!
    \x00\x01\xe4\xff

Creating Binary File Using Unicode With Ordinal > 255 Fails
    [Documentation]    FAIL STARTS: ValueError:
    Create Binary File    ${TESTFILE}    \u0100

Append To File
    Append To File    ${TESTFILE}    First line\n
    Append To File    ${TESTFILE}    Second line\n    ASCII
    Append To File    ${TESTFILE}    ${EMPTY}
    Append To File    ${TESTFILE}    Lääst läin
    Verify File    ${TESTFILE}    First line\nSecond line\nLääst läin

*** Keywords ***
Create And Verify File
    [Arguments]    ${content}=content    ${encoding}=UTF-8    ${file}=${TESTFILE}
    Create File    ${file}    ${content}    ${encoding}
    Verify File    ${file}    ${content}    ${encoding}

Create And Verify Binary File Using Bytes
    [Arguments]    ${content}    ${file}=${TESTFILE}
    ${content} =    Convert To Bytes    ${content}
    Create Binary File    ${file}    ${content}
    Verify Binary File    ${file}    ${content}

Create And Verify Binary File Using Unicode
    [Arguments]    ${content}    ${file}=${TESTFILE}
    Create Binary File    ${file}    ${content}
    ${expected} =    Convert To Bytes    ${content}
    Verify Binary File    ${file}    ${expected}

Verify Binary File
    [Arguments]    ${file}    ${expected}
    ${content} =    Get Binary File    ${file}
    Should Be Equal    ${content}    ${expected}

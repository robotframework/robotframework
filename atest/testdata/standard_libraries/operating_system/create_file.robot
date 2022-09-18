*** Settings ***
Suite Teardown    Remove Base Test Directory
Test Setup        Create Base Test Directory
Resource          os_resource.robot

*** Variables ***
${SYSTEM_ENCODING}          ASCII    # Should be overridden from CLI
${CONSOLE_ENCODING}         ASCII    # Should be overridden from CLI

*** Test Cases ***
Create File With Default Content
    Create File    ${TESTFILE}
    Verify File    ${TESTFILE}    ${EMPTY}

Create File With Content
    [Template]    Create and Verify File
    ${EMPTY}
    Content in one line
    Nön-ÄSCÏÏ Cöntënt

Create Multiline File
    [Template]    Create and Verify File
    Content in\n3\nlines.    expected=Content in${\n}3${\n}lines.
    1\n\n2\n\n\n3\n          expected=1${\n}${\n}2${\n}${\n}${\n}3${\n}
    CR\r\nLF                 expected=CR\r${\n}LF

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

Create File With System Encoding
    Create File    ${TESTFILE}    Nön-ÄSCÏÏ Cöntënt    encoding=SYSTEM
    Verify File    ${TESTFILE}    Nön-ÄSCÏÏ Cöntënt    encoding=${SYSTEM_ENCODING}

Create File With Console Encoding
    # Avoid content that the console encoding cannot handle by encoding
    # to bytes with an error handler and then decoding back to string.
    ${content} =    Encode string to bytes    Nön-ÄSCÏÏ Cöntënt    ${CONSOLE_ENCODING}    errors=ignore
    ${content} =    Decode bytes to string    ${content}    ${CONSOLE_ENCODING}
    Create File    ${TESTFILE}    ${content}    encoding=CONSole
    Verify File    ${TESTFILE}    ${content}    encoding=${CONSOLE_ENCODING}

Create File With Non-ASCII Name
    [Template]    Create and Verify File
    ASCII content    path=${NON ASCII}
    Спасибо          path=${NON ASCII}

Create File With Space In Name
    Create And Verify File    path=${WITH SPACE}

Create File To Non-Existing Directory
    Create And Verify File    path=${TESTDIR}${/}file.txt

Creating File Fails If Encoding Is Incorrect
    [Documentation]    FAIL REGEXP: Unicode(Encode|)Error: .*
    Create File    ${TESTFILE}    Hyvää yötä!    ASCII

Create Binary File Using Bytes
    [Template]    Create And Verify Binary File Using Bytes
    ${EMPTY}
    Hello, world!
    Hyvää yötä!
    \x00\x01\xe4\xff
    two\nlines
    \r\nfoo\n

Create Binary File Using Unicode
    [Template]    Create And Verify Binary File Using Unicode
    ${EMPTY}
    Hello, world!
    Hyvää yötä!
    \x00\x01\xe4\xff
    two\nlines
    \r\nfoo\n

Creating Binary File Using Unicode With Ordinal > 255 Fails
    [Documentation]    FAIL STARTS: ValueError:
    Create Binary File    ${TESTFILE}    \u0100

Append To File
    Append To File    ${TESTFILE}    First line\n
    Append To File    ${TESTFILE}    Second            ASCII
    Append To File    ${TESTFILE}    ${SPACE}line\n    SYSTEM
    Append To File    ${TESTFILE}    ${EMPTY}          CONSOLE
    Append To File    ${TESTFILE}    3\n\n
    Append To File    ${TESTFILE}    \n
    Append To File    ${TESTFILE}    Lääst läin\n\n    UTF-8
    Verify File       ${TESTFILE}    First line${\n}Second line${\n}3${\n}${\n}${\n}Lääst läin${\n}${\n}

Path as `pathlib.Path`
    Create And Verify File    path=${PATH/'file.txt'}
    Append To File    ${PATH/'file.txt'}    xxx
    Create And Verify Binary File Using Bytes    path=${PATH/'file.txt'}

*** Keywords ***
Create And Verify File
    [Arguments]    ${content}=content    ${encoding}=UTF-8    ${path}=${TESTFILE}    ${expected}=${content}
    Create File    ${path}    ${content}    ${encoding}
    Verify File    ${path}    ${expected}    ${encoding}

Create And Verify Binary File Using Bytes
    [Arguments]    ${content}=content    ${path}=${TESTFILE}
    ${content} =    Convert To Bytes    ${content}
    Create Binary File    ${path}    ${content}
    Verify Binary File    ${path}    ${content}

Create And Verify Binary File Using Unicode
    [Arguments]    ${content}    ${path}=${TESTFILE}
    Create Binary File    ${path}    ${content}
    ${expected} =    Convert To Bytes    ${content}
    Verify Binary File    ${path}    ${expected}

Verify Binary File
    [Arguments]    ${path}    ${expected}
    ${content} =    Get Binary File    ${path}
    Should Be Equal    ${content}    ${expected}

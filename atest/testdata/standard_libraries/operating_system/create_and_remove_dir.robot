*** Settings ***
Suite Teardown    Remove Base Test Directory
Test Setup        Create Base Test Directory
Resource          os_resource.robot

*** Test Cases ***
Create Directory
    Create Directory    ${TESTDIR}
    Directory Should Exist    ${TESTDIR}
    Create Directory    ${TESTDIR}
    Create Directory    ${TESTDIR}${/}sub${/}dirs${/}here
    Directory Should Exist    ${TESTDIR}${/}sub${/}dirs${/}here

Creating Directory Over Existing File Fails
    [Documentation]    FAIL Path '${TESTFILE}' already exists but is not a directory
    Create File    ${TESTFILE}
    Create Directory    ${TESTFILE}

Remove Directory
    Create Directory    ${TESTDIR}
    Directory Should Exist    ${TESTDIR}
    Remove Directory    ${TESTDIR}
    Should Not Exist    ${TESTDIR}

Remove Directory Recursively
    Create File    ${TESTDIR}${/}file.txt
    Create File    ${TESTDIR}${/}sub${/}file2.txt
    Remove Directory    ${TESTDIR}    Recursive
    Should Not Exist    ${TESTDIR}

Removing Non-Existing Directory Is Ok
    Remove Directory    non-existing-dir

Removing Non-Empty Directory When Not Recursive Fails
    [Documentation]    FAIL Directory '${TESTDIR}' is not empty.
    Create Directory    ${TESTDIR}
    Create File    ${TESTDIR}${/}file.txt
    Remove Directory    ${TESTDIR}    recursive=no

Empty Directory
    Create File    ${BASE}/file.txt
    Create File    ${BASE}/dir/f2
    Directory Should Not Be Empty    ${BASE}
    Empty Directory    ${BASE}
    Directory Should Be Empty    ${BASE}

Emptying Non-Existing Directory Fails
    [Documentation]    FAIL Directory '${BASE}${/}nonexisting' does not exist
    Empty Directory    ${BASE}/nonexisting

Emptying Dir When Directory Is File Fails
    [Documentation]    FAIL Directory '${TESTFILE}' does not exist
    Create File    ${TESTFILE}
    Empty Directory    ${TESTFILE}

Create And Remove Non-ASCII Directory
    Create Directory    ${NON ASCII}
    Directory Should Exist    ${NON ASCII}
    Remove Directory    ${NON ASCII}
    Should Not Exist    ${NON ASCII}

Create And Remove Directory With Space
    Create Directory    ${WITH SPACE}
    Directory Should Exist    ${WITH SPACE}
    Remove Directory    ${WITH SPACE}
    Should Not Exist    ${WITH SPACE}

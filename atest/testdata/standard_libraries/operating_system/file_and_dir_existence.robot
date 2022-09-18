*** Settings ***
Suite Teardown    Remove Base Test Directory
Test Setup        Create Base Test Directory
Resource          os_resource.robot

*** Test Cases ***
Should Exist
    [Documentation]    FAIL Path '${EXECDIR}${/}non-existing-file-or-dir' does not exist.
    Create File    ${TESTFILE}
    Create File    ${WITH SPACE}
    Create File    ${NON ASCII}
    Should Exist    ${TESTFILE}
    Should Exist    ${WITH SPACE}
    Should Exist    ${NON ASCII}
    Should Exist    ${CURDIR}
    Should Exist    non-existing-file-or-dir

Should Exist With Non Default Message
    [Documentation]    FAIL Non-default error message.
    Should Exist    non-existing-file-or-dir    Non-default error message.

Should Exist With Pattern
    [Documentation]    FAIL Path '${EXECDIR}${/}*non*existing*' does not exist.
    Create File    ${BASE}/file.txt
    Create Directory    ${BASE}/dir
    Should Exist    ${BASE}/*
    Should Exist    ${BASE}/*.txt
    Should Exist    ${BASE}${/}f*
    Should Exist    ${BASE}${/}d??
    Should Exist    ${BASE}${/}\[abcd]i[rst]
    Should Exist    ${EXECDIR}/*non*existing*

Glob In Name
    Create File    ${BASE}/[bar]foo.txt
    Create Directory    ${BASE}/[go]mo
    Should Exist    ${BASE}/[bar]foo.txt
    Should Exist    ${BASE}/[go]mo
    File Should Exist    ${BASE}/[bar]foo.txt
    Directory Should Exist    ${BASE}/[go]mo

Glob In Name Should Not Exist
    [Documentation]    FAIL Path '${BASE}${/}\[not]not.txt' matches '${BASE}${/}\[not]not.txt'.
    Create File    ${BASE}/[not]not.txt
    Should Not Exist    ${BASE}/[not]not.txt

Glob In Name File Should Not Exist
    [Documentation]    FAIL File '${BASE}${/}\[not]not2.txt' matches '${BASE}${/}\[not]not2.txt'.
    Create File    ${BASE}/[not]not2.txt
    File Should Not Exist    ${BASE}/[not]not2.txt

Glob In Name Directory Should Not Exist
    [Documentation]    FAIL Directory '${BASE}${/}\[not]not3' matches '${BASE}${/}\[not]not3'.
    Create Directory    ${BASE}/[not]not3
    Directory Should Not Exist    ${BASE}/[not]not3

Should Not Exist
    [Documentation]    FAIL Path '${CURDIR}' exists.
    Should Not Exist    ${TESTFILE}
    Should Not Exist    ${WITH SPACE}
    Should Not Exist    ${NON ASCII}
    Should Not Exist    ${CURDIR}

Should Not Exist With Non Default Message
    [Documentation]    FAIL This is a non-default error message!!
    Should Not Exist    ${CURDIR}    This is a non-default error message!!

Should Not Exist With Pattern
    [Documentation]    FAIL Path '${BASE}${/}f?' matches '${BASE}${/}f1' and '${BASE}${/}f2'.
    Should Not Exist    *non?existing*
    Create File    ${BASE}/f1
    Create File    ${BASE}/f2
    Should Not Exist    ${BASE}${/}f?

File Should Exist
    [Documentation]    FAIL File '${EXECDIR}${/}non-existing-file' does not exist.
    Create File    ${TESTFILE}
    Create File    ${WITH SPACE}
    Create File    ${NON ASCII}
    File Should Exist    ${TESTFILE}
    File Should Exist    ${WITH SPACE}
    File Should Exist    ${NON ASCII}
    File Should Exist    non-existing-file

File Should Exist When Dir Exists
    [Documentation]    FAIL File '${CURDIR}' does not exist.
    File Should Exist    ${CURDIR}

File Should Exist With Non Default Message
    [Documentation]    FAIL Hello, this is a non-default error
    File Should Exist    ${CURDIR}    Hello, this is a non-default error

File Should Exist With Pattern
    [Documentation]    FAIL File '${BASE}${/}d??' does not exist.
    Create File    ${BASE}/file.txt
    Create Directory    ${BASE}/dir
    File Should Exist    ${BASE}/*
    File Should Exist    ${BASE}/f[!abcd]l[efgh].???
    File Should Exist    ${BASE}${/}d??

File Should Not Exist
    [Documentation]    FAIL File '${TESTFILE}' exists.
    File Should Not Exist    ${WITH SPACE}
    File Should Not Exist    ${NON ASCII}
    File Should Not Exist    ${CURDIR}
    Create File    ${TESTFILE}    whatever
    File Should Not Exist    ${TESTFILE}

File Should Not Exist With Non Default Message
    [Documentation]    FAIL My non-default
    Create File    ${TESTFILE}    whatever
    File Should Not Exist    ${TESTFILE}    My non-default

File Should Not Exist With Pattern Matching One File
    [Documentation]    FAIL File '${BASE}${/}*.txt' matches '${BASE}${/}file.txt'.
    Create File    ${BASE}/file.txt
    Create Directory    ${BASE}/dir
    File Should Not Exist    *non?existing*
    File Should Not Exist    ${BASE}${/}dir
    File Should Not Exist    ${BASE}/*.txt

File Should Not Exist With Pattern Matching Multiple Files
    [Documentation]    FAIL File '${BASE}${/}f*.txt' matches '${BASE}${/}f1.txt' and '${BASE}${/}f2.txt'.
    Create File    ${BASE}/f1.txt
    Create File    ${BASE}/f2.txt
    File Should Not Exist    ${BASE}/f*.txt

Directory Should Exist
    [Documentation]    FAIL Directory '${EXECDIR}${/}non-existing-directory' does not exist.
    Create Directory    ${NON ASCII}
    Create Directory    ${WITH SPACE}
    Directory Should Exist    %{TEMPDIR}
    Directory Should Exist    ${NON ASCII}
    Directory Should Exist    ${WITH SPACE}
    Directory Should Exist    non-existing-directory

Directory Should Exist When File Exists
    [Documentation]    FAIL Directory '${TESTFILE}' does not exist.
    Create File    ${TESTFILE}
    Directory Should Exist    ${TESTFILE}

Directory Should Exist Exists With Non Default Message
    [Documentation]    FAIL One more non-default error
    Directory Should Exist    non-existing-directory    One more non-default error

Directory Should Exist With Pattern
    [Documentation]    FAIL Directory '${BASE}${/}f*' does not exist.
    Create File    ${BASE}/file.txt
    Create Directory    ${BASE}/dir
    Directory Should Exist    ${BASE}${/}*
    Directory Should Exist    ${BASE}/d[!whatever]?
    Directory Should Exist    ${BASE}/f*

Directory Should Not Exist
    [Documentation]    FAIL Directory '${CURDIR}' exists.
    Create File    ${TESTFILE}
    Directory Should Not Exist    non-existing
    Directory Should Not Exist    ${TESTFILE}
    Directory Should Not Exist    ${NON ASCII}
    Directory Should Not Exist    ${WITH SPACE}
    Directory Should Not Exist    ${CURDIR}

Directory Should Not Exist With Non Default Message
    [Documentation]    FAIL Still one more non-default msg
    Directory Should Not Exist    ${CURDIR}    Still one more non-default msg

Directory Should Not Exist With Pattern Matching One Dir
    [Documentation]    FAIL Directory '${BASE}${/}d*' matches '${BASE}${/}dir'.
    Create File    ${BASE}/file.txt
    Create Directory    ${BASE}/dir
    Directory Should Not Exist    *non?existing*
    Directory Should Not Exist    ${BASE}${/}file.txt
    Directory Should Not Exist    ${BASE}/d*

Directory Should Not Exist With Pattern Matching Multiple Dirs
    [Documentation]    FAIL Directory '${BASE}${/}*r' matches '${BASE}${/}another' and '${BASE}${/}dir'.
    Create Directory    ${BASE}/dir
    Create Directory    ${BASE}/another
    Directory Should Not Exist    ${BASE}${/}*r

Path as `pathlib.Path`
    Create File                   ${BASE}/file.txt
    File Should Exist             ${PATH/'file.txt'}
    Directory Should Not Exist    ${PATH/'file.txt'}
    Should Exist                  ${PATH/'file.txt'}
    File Should Not Exist         ${PATH}
    Directory Should Exist        ${PATH}
    Should Exist                  ${PATH}
    File Should Not Exist         ${PATH/'nonex'}
    Directory Should Not Exist    ${PATH/'nonex'}
    Should Not Exist              ${PATH/'nonex'}

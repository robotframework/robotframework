*** Settings ***
Test Setup      Create Base Test Directory
Suite Teardown  Remove Base Test Directory
Resource        os_resource.robot

*** Test Cases ***
Should Exist
    [Documentation]  FAIL REGEXP: Path '${ANYDIR}non-existing-file-or-dir' does not match any file or directory
    Create File   ${TESTFILE}
    Create File   ${WITH SPACE}
    Create File   ${NON ASCII}
    Should Exist  ${TESTFILE}
    Should Exist  ${WITH SPACE}
    Should Exist  ${NON ASCII}
    Should Exist  ${CURDIR}
    Should Exist  non-existing-file-or-dir

Should Exist With Non Default Message
    [Documentation]  FAIL Non-default error message
    Should Exist  non-existing-file-or-dir  Non-default error message

Should Exist With Pattern
    [Documentation]  FAIL REGEXP: Path '${ANYDIR}\\*non\\*existing\\*' does not match any file or directory
    Create File  ${BASE}/file.txt
    Create Directory  ${BASE}/dir
    Should Exist  ${BASE}/*
    Should Exist  ${BASE}/*.txt
    Should Exist  ${BASE}${/}f*
    Should Exist  ${BASE}${/}d??
    Should Exist  ${BASE}${/}[abcd]i[rst]
    Should Exist  *non*existing*

Should Not Exist
    [Documentation]  FAIL Path '${CURDIR}' exists
    Should Not Exist  ${TESTFILE}
    Should Not Exist  ${WITH SPACE}
    Should Not Exist  ${NON ASCII}
    Should Not Exist  ${CURDIR}

Should Not Exist With Non Default Message
    [Documentation]  FAIL This is a non-default error message
    Should Not Exist  ${CURDIR}  This is a non-default error message

Should Not Exist With Pattern
    [Documentation]  FAIL Path '${BASE}${/}f?' matches '${BASE}${/}f1' and '${BASE}${/}f2'
    Should Not Exist  *non?existing*
    Create File  ${BASE}/f1
    Create File  ${BASE}/f2
    Should Not Exist  ${BASE}${/}f?

File Should Exist
    [Documentation]  FAIL REGEXP: Path '${ANYDIR}non-existing-file' does not match any file
    Create File  ${TESTFILE}
    Create File   ${WITH SPACE}
    Create File   ${NON ASCII}
    File Should Exist  ${TESTFILE}
    File Should Exist  ${WITH SPACE}
    File Should Exist  ${NON ASCII}
    File Should Exist  non-existing-file

File Should Exist When Dir Exists
    [Documentation]  FAIL Path '${CURDIR}' does not match any file
    File Should Exist  ${CURDIR}

File Should Exist With Non Default Message
    [Documentation]  FAIL Hello, this is a non-default error
    File Should Exist  ${CURDIR}  Hello, this is a non-default error

File Should Exist With Pattern
    [Documentation]  FAIL Path '${BASE}${/}d??' does not match any file
    Create File  ${BASE}/file.txt
    Create Directory  ${BASE}/dir
    File Should Exist  ${BASE}/*
    File Should Exist  ${BASE}/f[!abcd]l[efgh].???
    File Should Exist  ${BASE}${/}d??

File Should Not Exist
    [Documentation]  FAIL File '${TESTFILE}' exists
    File Should Not Exist  ${WITH SPACE}
    File Should Not Exist  ${NON ASCII}
    File Should Not Exist  ${CURDIR}
    Create File  ${TESTFILE}  whatever
    File Should Not Exist  ${TESTFILE}

File Should Not Exist With Non Default Message
    [Documentation]  FAIL My non-default
    Create File  ${TESTFILE}  whatever
    File Should Not Exist  ${TESTFILE}  My non-default

File Should Not Exist With Pattern Matching One File
    [Documentation]  FAIL Path '${BASE}${/}*.txt' matches file '${BASE}${/}file.txt'
    Create File  ${BASE}/file.txt
    Create Directory  ${BASE}/dir
    File Should Not Exist  *non?existing*
    File Should Not Exist  ${BASE}${/}dir
    File Should Not Exist  ${BASE}/*.txt

File Should Not Exist With Pattern Matching Multiple Files
    [Documentation]  FAIL Path '${BASE}${/}f*.txt' matches files '${BASE}${/}f1.txt' and '${BASE}${/}f2.txt'
    Create File  ${BASE}/f1.txt
    Create File  ${BASE}/f2.txt
    File Should Not Exist  ${BASE}/f*.txt

Directory Should Exist
    [Documentation]  FAIL REGEXP: Path '${ANYDIR}non-existing-directory' does not match any directory
    Create Directory  ${NON ASCII}
    Create Directory  ${WITH SPACE}
    Directory Should Exist  %{TEMPDIR}
    Directory Should Exist  ${NON ASCII}
    Directory Should Exist  ${WITH SPACE}
    Directory Should Exist  non-existing-directory

Directory Should Exist When File Exists
    [Documentation]  FAIL Path '${TESTFILE}' does not match any directory
    Create File  ${TESTFILE}
    Directory Should Exist  ${TESTFILE}

Directory Should Exist Exists With Non Default Message
    [Documentation]  FAIL One more non-default error
    Directory Should Exist  non-existing-directory  One more non-default error

Directory Should Exist With Pattern
    [Documentation]  FAIL Path '${BASE}${/}f*' does not match any directory
    Create File  ${BASE}/file.txt
    Create Directory  ${BASE}/dir
    Directory Should Exist  ${BASE}${/}*
    Directory Should Exist  ${BASE}/d[!whatever]?
    Directory Should Exist  ${BASE}/f*

Directory Should Not Exist
    [Documentation]  FAIL Directory '${CURDIR}' exists
    Create File  ${TESTFILE}
    Directory Should Not Exist  non-existing
    Directory Should Not Exist  ${TESTFILE}
    Directory Should Not Exist  ${NON ASCII}
    Directory Should Not Exist  ${WITH SPACE}
    Directory Should Not Exist  ${CURDIR}

Directory Should Not Exist With Non Default Message
    [Documentation]  FAIL Still one more non-default msg
    Directory Should Not Exist  ${CURDIR}  Still one more non-default msg

Directory Should Not Exist With Pattern Matching One Dir
    [Documentation]  FAIL Path '${BASE}${/}d*' matches directory '${BASE}${/}dir'
    Create File  ${BASE}/file.txt
    Create Directory  ${BASE}/dir
    Directory Should Not Exist  *non?existing*
    Directory Should Not Exist  ${BASE}${/}file.txt
    Directory Should Not Exist  ${BASE}/d*

Directory Should Not Exist With Pattern Matching Multiple Dirs
    [Documentation]  FAIL Path '${BASE}${/}*r' matches directories '${BASE}${/}another' and '${BASE}${/}dir'
    Create Directory  ${BASE}/dir
    Create Directory  ${BASE}/another
    Directory Should Not Exist  ${BASE}${/}*r


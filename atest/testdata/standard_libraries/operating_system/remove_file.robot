*** Settings ***
Suite Teardown    Remove Base Test Directory
Test Setup        Create Base Test Directory
Resource          os_resource.robot

*** Test Cases ***
Remove File
    Create File    ${TESTFILE}
    File Should Exist    ${TESTFILE}
    Remove File    ${TESTFILE}
    Should Not Exist    ${TESTFILE}

Remove Files
    Create File    ${BASE}/foo.txt
    Create File    ${BASE}/bar.txt
    Create File    ${BASE}/zap.txt
    Remove Files    ${BASE}${/}foo.txt    ${BASE}/./bar.txt    ${BASE}/zap.txt
    Should Not Exist    ${BASE}/foo.txt
    Should Not Exist    ${BASE}/bar.txt
    Should Not Exist    ${BASE}/zap.txt

Remove Non-ASCII File
    Create File    ${NONASCII}
    File Should Exist    ${NONASCII}
    Remove File    ${NONASCII}
    Should Not Exist    ${NONASCII}

Remove File With Space
    Create File    ${WITHSPACE}
    File Should Exist    ${WITHSPACE}
    Remove File    ${WITHSPACE}
    Should Not Exist    ${WITHSPACE}

Remove Files Using Glob Pattern
    Create File    ${BASE}/file-1.txt
    Create File    ${BASE}/file 2.txt
    Create File    ${BASE}/myfile.txt
    Remove File    ${BASE}/file??.txt
    Directory Should Have Items    ${BASE}    myfile.txt
    Remove File    ${BASE}/*.txt
    Directory Should Be Empty    ${BASE}

Remove Non-ASCII Files Using Glob Pattern
    Create File    ${BASE}/file
    Create File    ${BASE}/fïlë
    Create File    ${BASE}/fílé
    Remove Files    ${BASE}/*e    ${BASE}/???ë
    Directory Should Have Items    ${BASE}    fílé
    Remove File    ${BASE}${/}f*
    Directory Should Be Empty    ${BASE}

Remove Non-Existing File
    Remove File    non-existing.txt

Removing Directory As A File Fails
    [Documentation]    FAIL Path '${CURDIR}' is not a file.
    Remove File    ${CURDIR}

Remove file containing glob pattern
    Create File    ${BASE}/[foo]bar.txt
    File Should Exist    ${BASE}/[foo]bar.txt
    Remove File    ${BASE}/[foo]bar.txt
    Should Not Exist    ${BASE}/[foo]bar.txt

Path as `pathlib.Path`
    Create File         ${BASE}/file1.txt
    Create File         ${BASE}/file2.txt
    Create File         ${BASE}/file3.txt
    Create File         ${BASE}/file4.txt
    Remove File         ${PATH/'file1.txt'}
    Remove Files        ${PATH/'file2.txt'}    ${PATH/'file[34].txt'}
    Should Not Exist    ${BASE}/file*.txt

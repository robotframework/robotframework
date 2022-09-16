*** Settings ***
Suite Teardown    Remove Base Test Directory
Test Setup        Create Base Test Directory
Resource          os_resource.robot

*** Test Cases ***
Move File
    Create File    ${TESTFILE}    contents
    Move File    ${TESTFILE}    ${TESTFILE2}
    Should Not Exist    ${TESTFILE}
    Verify File    ${TESTFILE2}    contents

Copy File
    Create File    ${TESTFILE}    contents
    Copy File    ${TESTFILE}    ${TESTFILE2}
    Verify File    ${TESTFILE2}    contents
    Directory Should Have Items    ${BASE}    ${TESTFILE SHORT NAME}    ${TESTFILE 2 SHORT NAME}

Copy File With Glob Pattern
    Create File    ${BASE}/somefile.txt    contents
    Copy File    ${BASE}/som*i??.txt    ${TESTFILE}
    Verify File    ${TESTFILE}    contents
    Directory Should Have Items    ${BASE}    ${TESTFILE SHORT NAME}    somefile.txt

Move File With Glob Pattern
    Create File    ${BASE}/somefile.txt    contents
    Move File    ${BASE}/s?me?i??.txt    ${TESTFILE}
    Verify File    ${TESTFILE}    contents
    Should Not Exist    ${BASE}/somefile.txt

Move File With Glob Pattern With Multiple Matches Fails
    [Documentation]    FAIL Multiple matches with source pattern '${BASE}${/}file*.txt'.
    Create File    ${BASE}/file1.txt    contents
    Create File    ${BASE}/file2.txt    contents
    Move File    ${BASE}/file*.txt    somewhere

Copy File With Glob Pattern With Multiple Matches Fails
    [Documentation]    FAIL Multiple matches with source pattern '${BASE}${/}file*.txt'.
    Create File    ${BASE}/file1.txt    contents
    Create File    ${BASE}/file2.txt    contents
    Copy File    ${BASE}/file*.txt    somewhere

Copy File With Glob Pattern With No Matches Fails
    [Documentation]    FAIL Source file '${EXECDIR}${/}zoo*bar?not*here' does not exist.
    Copy File    ${EXECDIR}/zoo*bar?not*here    somewhere

Move File With Glob Pattern With No Matches Fails
    [Documentation]    FAIL Source file '${EXECDIR}${/}zoo*bar?not*here' does not exist.
    Move File    ${EXECDIR}/zoo*bar?not*here    somewhere

Copy File when destination exists should be ok
    Create File    ${TESTFILE}    contents
    Copy File    ${TESTFILE}    ${TESTFILE2}
    Create File    ${TESTFILE}    contents2
    Copy File    ${TESTFILE}    ${TESTFILE2}
    Verify File    ${TESTFILE2}    contents2

Copy File when destination is a directory
    ${destination}=    Set Variable    ${BASE}/foo
    Create Directory    ${destination}
    Create File    ${TESTFILE}    contents
    Copy File    ${TESTFILE}    ${destination}
    Verify File    ${destination}${/}${TESTFILE SHORT NAME}    contents

Copy File when destination is a directory and file with same name exists
    ${destination}=    Set Variable    ${BASE}/foo
    Create Directory    ${destination}
    Create File    ${TESTFILE}    contents
    Create File    ${destination}${/}${TESTFILE SHORT NAME}    original
    Copy File    ${TESTFILE}    ${destination}
    Verify File    ${destination}${/}${TESTFILE SHORT NAME}    contents

Move File To Existing Directory
    Create Directory    ${BASE}/foo
    Create Directory    ${BASE}/bar
    Create File    ${BASE}/zap    contents
    Move File    ${BASE}/zap    ${BASE}${/}foo${/}file
    Should Not Exist    ${BASE}/zap
    Verify File    ${BASE}/foo/file    contents
    Move File    ${BASE}/foo${/}file    ${BASE}/bar
    Should Not Exist    ${BASE}/foo/bar
    Verify File    ${BASE}/bar/file    contents

Move File To Non-Existing Directory
    Directory Should Not Exist    ${BASE}/*
    Create File    ${TESTFILE}    contents
    Move File    ${TESTFILE}    ${BASE}${/}dir/new.file
    Should Not Exist    ${TESTFILE}
    Verify File    ${BASE}/dir/new.file    contents
    Move File    ${BASE}/dir/new.file    ${BASE}${/}dir2${/}
    Should Not Exist    ${BASE}/dir/new.file
    Verify File    ${BASE}/dir2/new.file    contents

Move File Using Just File Name
    Create File    rf_test.1    contents
    ${contents 1} =    Get File    rf_test.1
    Move File    rf_test.1    rf_test.2
    Should Not Exist    rf_test.1
    Should Exist    ${EXECDIR}/rf_test.2
    ${contents 2} =    Get File    rf_test.2
    Should Be Equal    -${contents 1}-${contents 2}-    -contents-contents-
    [Teardown]    Remove Files    rf_test.1    rf_test.2

Moving Non-Existing File Fails
    [Documentation]    FAIL Source file '${EXECDIR}${/}non-existing-file.txt' does not exist.
    Move File    non-existing-file.txt    whatever.txt

Name Contains Glob
    Create File    ${BASE}/[ke]kkonen.txt
    Copy File    ${BASE}/[ke]kkonen.txt    ${BASE}/[ke]kkonen-2.txt
    Should Exist    ${BASE}/[ke]kkonen.txt
    Should Exist    ${BASE}/[ke]kkonen-2.txt
    Move File    ${BASE}/[ke]kkonen.txt    ${BASE}/[ke]kkonen-3.txt
    Should Not Exist    ${BASE}/[ke]kkonen.txt
    Should Exist    ${BASE}/[ke]kkonen-2.txt
    Should Exist    ${BASE}/[ke]kkonen-3.txt

Copy File to same path
    Create File    ${BASE}/file.txt
    Copy File    ${BASE}/file.txt    ${BASE}/file.txt
    Directory Should Have Items    ${BASE}    file.txt

Move File to same path
    Create File    ${BASE}/file.txt
    Move File    ${BASE}/file.txt    ${BASE}/./file.txt
    Directory Should Have Items    ${BASE}    file.txt

Copy File to same directory
    Create File    ${BASE}/file.txt
    Copy File    ${BASE}/file.txt    ${BASE}/./
    Directory Should Have Items    ${BASE}    file.txt

Move File to same directory
    Create File    ${BASE}/file.txt
    Move File    ${BASE}/dir/../file.txt    ${BASE}
    Directory Should Have Items    ${BASE}    file.txt

Copy File to same path with different case on Windows
    Create File    ${BASE}/file.txt
    Copy File    ${BASE}/file.txt    ${BASE}/FILE.TXT

Move File to same path with different case on Windows
    Create File    ${BASE}/file.txt
    Move File    ${BASE}/file.txt    ${BASE}/FILE.TXT

Copy File to same path when file doesn't exist
    [Documentation]    FAIL Source file '${EXECDIR}${/}non-existing.file' does not exist.
    Copy File    non-existing.file    non-existing.file

Move File to same path when file doesn't exist
    [Documentation]    FAIL Source file '${EXECDIR}${/}path${/}non-existing.file' does not exist.
    Move File    path/non-existing.file    path/non-existing.file

Move File returns destination path
    Create File    ${BASE}/f1.txt
    Create File    ${BASE}/f2.txt
    Create Directory    ${BASE}/dir
    ${path} =    Move File    ${BASE}/f1.txt    ${BASE}/./new.txt
    Should Be Equal    ${path}    ${BASE}${/}new.txt
    ${path} =    Move File    ${BASE}/f*.txt    ${BASE}/dir
    Should Be Equal    ${path}    ${BASE}${/}dir${/}f2.txt

Copy File returns destination path
    Create File    ${BASE}/file.txt
    Create Directory    ${BASE}/dir
    ${path} =    Copy File    ${BASE}/file.txt    ${BASE}/./new.txt
    Should Be Equal    ${path}    ${BASE}${/}new.txt
    ${path} =    Copy File    ${BASE}/f*.txt    ${BASE}/dir
    Should Be Equal    ${path}    ${BASE}${/}dir${/}file.txt

Path as `pathlib.Path`
    Create File              ${BASE}/file
    Move File                ${PATH/'file'}    ${PATH/'new'}
    Copy File                ${PATH/'new'}    ${PATH/'copy'}
    File Should Not Exist    ${BASE}/file
    File Should Exist        ${BASE}/new
    File Should Exist        ${BASE}/copy

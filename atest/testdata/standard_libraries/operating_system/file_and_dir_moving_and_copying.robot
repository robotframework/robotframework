*** Settings ***
Test Setup      Create Base Test Directory
Suite Teardown  Remove Base Test Directory
Resource        os_resource.robot

*** Test Cases ***
Move File
    Create File  ${TESTFILE}  contents
    Move File  ${TESTFILE}  ${TESTFILE2}
    Should Not Exist  ${TESTFILE}
    Verify File  ${TESTFILE2}  contents

Copy File
    Create File  ${TESTFILE}  contents
    Copy File  ${TESTFILE}  ${TESTFILE2}
    Verify File  ${TESTFILE2}  contents
    Directory Should Have Items   ${BASE}    ${TESTFILE SHORT NAME}    ${TESTFILE 2 SHORT NAME}

Copy File With Glob Pattern
    Create File  ${BASE}/somefile.txt  contents
    Copy File  ${BASE}/som*i??.txt  ${TESTFILE}
    Verify File  ${TESTFILE}  contents
    Directory Should Have Items   ${BASE}    ${TESTFILE SHORT NAME}    somefile.txt

Move File With Glob Pattern
    Create File  ${BASE}/somefile.txt  contents
    Move File  ${BASE}/s?me?i??.txt  ${TESTFILE}
    Verify File  ${TESTFILE}  contents
    Should Not Exist  ${BASE}/somefile.txt

Move File With Glob Pattern With Multiple Matches Fails
    [Documentation]  FAIL REGEXP: Multiple matches with source pattern '.*file\\*\\.txt'
    Create File  ${BASE}/file1.txt  contents
    Create File  ${BASE}/file2.txt  contents
    Move File   ${BASE}/file*.txt   somewhere

Copy File With Glob Pattern With Multiple Matches Fails
    [Documentation]  FAIL REGEXP: Multiple matches with source pattern '.*file\\*\\.txt'
    Create File  ${BASE}/file1.txt  contents
    Create File  ${BASE}/file2.txt  contents
    Copy File   ${BASE}/file*.txt   somewhere

Copy File With Glob Pattern With No Matches Fails
    [Documentation]  FAIL Source file 'zoo*bar*not*here' does not exist
    Copy File   zoo*bar*not*here    somewhere

Move File With Glob Pattern With No Matches Fails
    [Documentation]  FAIL Source file 'foo*bar?zoo*not*here' does not exist
    Move File   foo*bar?zoo*not*here    somewhere

Copy File when destination exists should be ok
    Create File  ${TESTFILE}  contents
    Copy File  ${TESTFILE}  ${TESTFILE2}
    Create File  ${TESTFILE}  contents2
    Copy File  ${TESTFILE}  ${TESTFILE2}
    Verify File  ${TESTFILE2}  contents2

Copy File when destination is a directory
    ${destination}=    Set Variable    ${BASE}/foo
    Create Directory   ${destination}
    Create File  ${TESTFILE}  contents
    Copy File    ${TESTFILE}  ${destination}
    Verify File  ${destination}${/}${TESTFILE SHORT NAME}   contents

Copy File when destination is a directory and file with same name exists
    ${destination}=    Set Variable    ${BASE}/foo
    Create Directory   ${destination}
    Create File  ${TESTFILE}  contents
    Create File  ${destination}${/}${TESTFILE SHORT NAME}   original
    Copy File    ${TESTFILE}  ${destination}
    Verify File  ${destination}${/}${TESTFILE SHORT NAME}   contents

Move File To Existing Dir
    Create Directory  ${BASE}/foo
    Create Directory  ${BASE}/bar
    Create File  ${BASE}/zap  contents
    Move File  ${BASE}/zap  ${BASE}${/}foo${/}file
    Should Not Exist  ${BASE}/zap
    Verify File  ${BASE}/foo/file  contents
    Move File  ${BASE}/foo${/}file  ${BASE}/bar
    Should Not Exist  ${BASE}/foo/bar
    Verify File  ${BASE}/bar/file  contents

Move File To Non-Existing Dir
    Directory Should Not Exist  ${BASE}/*
    Create File  ${TESTFILE}  contents
    Move File  ${TESTFILE}  ${BASE}${/}dir/new.file
    Should Not Exist  ${TESTFILE}
    Verify File  ${BASE}/dir/new.file  contents
    Move File  ${BASE}/dir/new.file  ${BASE}${/}dir2${/}
    Should Not Exist  ${BASE}/dir/new.file
    Verify File  ${BASE}/dir2/new.file  contents

Move File Using Just File Name
    Create File  rf_test.1  contents
    ${contents 1} =  Get File  rf_test.1
    Move File  rf_test.1  rf_test.2
    Should Not Exist  rf_test.1
    Should Exist  ${EXECDIR}/rf_test.2
    ${contents 2} =  Get File  rf_test.2
    Should Be Equal  -${contents 1}-${contents 2}-  -contents-contents-
    [Teardown]  Remove Files  rf_test.1  rf_test.2

Moving Non-Existing File Fails
    [Documentation]  FAIL REGEXP: Source file 'non-existing-file.txt' does not exist
    Move File  non-existing-file.txt  whatever.txt

Move Directory
    Create File  ${BASE}/dir/f1      file1
    Create File  ${BASE}/dir/sub/f2  file2
    Move Directory  ${BASE}/dir  ${BASE}/dir2
    Should Not Exist  ${BASE}/dir
    Verify File  ${BASE}/dir2/f1      file1
    Verify File  ${BASE}/dir2/sub/f2  file2

Move Directory To Existing Dir
    Create File  ${BASE}/dir/f1      file1
    Create File  ${BASE}/dir/sub/f2  file2
    Create File  ${BASE}/dir2/f3     file3
    Create Directory  ${BASE}/dir2
    Move Directory  ${BASE}/dir  ${BASE}/dir2
    Should Not Exist  ${BASE}/dir
    Verify File  ${BASE}/dir2/dir/f1      file1
    Verify File  ${BASE}/dir2/dir/sub/f2  file2
    Verify File  ${BASE}/dir2/f3          file3

Move Directory To Non-Existing Dir Tree
    Create File  ${BASE}/dir/file  content
    Move Directory  ${BASE}${/}dir  ${BASE}/1/2/3/4/5
    Should Not Exist  ${BASE}/dir
    Verify File  ${BASE}/1/2/3/4/5/file  content

Move Directory Using Just Dir Name
    Create File  rf_test_1/file  contents
    ${contents 1} =  Get File  rf_test_1/file
    Move Directory  rf_test_1  rf_test_2
    Should Not Exist  rf_test_1
    Should Exist  ${EXECDIR}/rf_test_2
    ${contents 2} =  Get File  rf_test_2/file
    Should Be Equal  -${contents 1}-${contents 2}-  -contents-contents-
    [Teardown]  Remove Just Name Dirs

Moving Non-Existing Directory Fails
    [Documentation]  FAIL REGEXP: Source directory '${ANYDIR}non-existing-dir' does not exist
    Move Directory  non-existing-dir  whatever

***Keywords***
Remove Just Name Dirs
    Remove Directory  rf_test_1  recursive
    Remove Directory  rf_test_2  recursive

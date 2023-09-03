*** Settings ***
Suite Teardown    Remove Base Test Directory
Test Setup        Create Base Test Directory
Resource          os_resource.robot

*** Test Cases ***
Move Directory
    Create File    ${BASE}/dir/f1    file1
    Create File    ${BASE}/dir/sub/f2    file2
    Move Directory    ${BASE}/dir    ${BASE}/dir2
    Should Not Exist    ${BASE}/dir
    Verify File    ${BASE}/dir2/f1    file1
    Verify File    ${BASE}/dir2/sub/f2    file2

Copy Directory
    Create File    ${BASE}/dir/f1    file1
    Create File    ${BASE}/dir/sub/f2    file2
    Copy Directory    ${BASE}/dir    ${BASE}/dir2
    Should Exist    ${BASE}/dir
    Verify File    ${BASE}/dir2/f1    file1
    Verify File    ${BASE}/dir2/sub/f2    file2

Move Directory To Existing Directory
    Create File    ${BASE}/dir/f1    file1
    Create File    ${BASE}/dir/sub/f2    file2
    Create File    ${BASE}/dir2/f3    file3
    Create Directory    ${BASE}/dir2
    Move Directory    ${BASE}/dir    ${BASE}/dir2
    Should Not Exist    ${BASE}/dir
    Verify File    ${BASE}/dir2/dir/f1    file1
    Verify File    ${BASE}/dir2/dir/sub/f2    file2
    Verify File    ${BASE}/dir2/f3    file3

Copy Directory To Existing Directory
    Create File    ${BASE}/dir/f1    file1
    Create File    ${BASE}/dir/sub/f2    file2
    Create File    ${BASE}/dir2/f3    file3
    Create Directory    ${BASE}/dir2
    Copy Directory    ${BASE}/dir    ${BASE}/dir2
    Should Exist    ${BASE}/dir
    Verify File    ${BASE}/dir2/dir/f1    file1
    Verify File    ${BASE}/dir2/dir/sub/f2    file2
    Verify File    ${BASE}/dir2/f3    file3

Move Directory To Non-Existing Directory Tree
    Create File    ${BASE}/dir/file    content
    Move Directory    ${BASE}${/}dir    ${BASE}/1/2/3/4/5
    Should Not Exist    ${BASE}/dir
    Verify File    ${BASE}/1/2/3/4/5/file    content

Copy Directory To Non-Existing Directory Tree
    Create File    ${BASE}/dir/file    content
    Copy Directory    ${BASE}${/}dir    ${BASE}/1/2/3/4/5
    Should Exist    ${BASE}/dir
    Verify File    ${BASE}/1/2/3/4/5/file    content

Move Directory Using Just Directory Name
    Create File    rf_test_1/file    contents
    ${contents 1} =    Get File    rf_test_1/file
    Move Directory    rf_test_1    rf_test_2
    Should Not Exist    rf_test_1
    Should Exist    ${EXECDIR}/rf_test_2
    ${contents 2} =    Get File    rf_test_2/file
    Should Be Equal    -${contents 1}-${contents 2}-    -contents-contents-
    [Teardown]    Remove Just Name Dirs

Copy Directory Using Just Directory Name
    Create File    rf_test_1/file    contents
    ${contents 1} =    Get File    rf_test_1/file
    Copy Directory    rf_test_1    rf_test_2
    Should Exist    rf_test_1
    Should Exist    ${EXECDIR}/rf_test_2
    ${contents 2} =    Get File    rf_test_2/file
    Should Be Equal    -${contents 1}-${contents 2}-    -contents-contents-
    [Teardown]    Remove Just Name Dirs

Moving Non-Existing Directory Fails
    [Documentation]    FAIL Source '${EXECDIR}${/}non-existing-dir' does not exist.
    Move Directory    non-existing-dir    whatever

Copying Non-Existing Directory Fails
    [Documentation]    FAIL Source '${EXECDIR}${/}non-existing-dir' does not exist.
    Copy Directory    non-existing-dir    whatever

Path as `pathlib.Path`
    Create Directory              ${BASE}/dir
    Move Directory                ${PATH/'dir'}    ${PATH/'new'}
    Copy Directory                ${PATH/'new'}    ${PATH/'copy'}
    Directory Should Not Exist    ${BASE}/dir
    Directory Should Exist        ${BASE}/new
    Directory Should Exist        ${BASE}/copy

*** Keywords ***
Remove Just Name Dirs
    Remove Directory    rf_test_1    recursive
    Remove Directory    rf_test_2    recursive

*** Settings ***
Suite Teardown    Remove Base Test Directory
Test Setup        Create Base Test Directory
Resource          os_resource.robot

*** Test Cases ***
Directory Should Be Empty
    [Documentation]    FAIL Directory '${BASE}' is not empty. Contents: 'dir', 'file.txt', 'nöẗ önlÿ äscïï'.
    Test Directory Should Be Empty    ${BASE}

Non-ASCII Directory Should Be Empty
    [Documentation]    FAIL Directory '${NON ASCII}' is not empty. Contents: 'dir', 'file.txt', 'nöẗ önlÿ äscïï'.
    Test Directory Should Be Empty    ${NON ASCII}

Directory With Space Should Be Empty
    [Documentation]    FAIL Directory '${WITH SPACE}' is not empty. Contents: 'dir', 'file.txt', 'nöẗ önlÿ äscïï'.
    Test Directory Should Be Empty    ${WITH SPACE}

Directory Should Be Empty When Directory Does Not Exist
    [Documentation]    FAIL Directory '${NON ASCII}' does not exist.
    Directory Should Be Empty    ${NON ASCII}

Directory Should Not Be Empty
    [Documentation]    FAIL Directory '${BASE}' is empty.
    Test Directory Should Not Be Empty    ${BASE}

Non-ASCII Directory Should Not Be Empty
    [Documentation]    FAIL Directory '${NON ASCII}' is empty.
    Test Directory Should Not Be Empty    ${NON ASCII}

Directory With Space Should Not Be Empty
    [Documentation]    FAIL Directory '${WITH SPACE}' is empty.
    Test Directory Should Not Be Empty    ${WITH SPACE}

Directory Should Not Be Empty When Directory Does Not Exist
    [Documentation]    FAIL Directory '${NON ASCII}' does not exist.
    Directory Should Not Be Empty    ${NON ASCII}

File Should Be Empty
    [Documentation]    FAIL File '${TESTFILE}' is not empty. Size: 12 bytes.
    Test File Should Be Empty    ${TESTFILE}

Non-ASCII File Should Be Empty
    [Documentation]    FAIL File '${NON ASCII}' is not empty. Size: 12 bytes.
    Test File Should Be Empty    ${NON ASCII}

File With Space Should Be Empty
    [Documentation]    FAIL File '${WITH SPACE}' is not empty. Size: 12 bytes.
    Test File Should Be Empty    ${WITH SPACE}

File Should Be Empty When File Does Not Exist
    [Documentation]    FAIL File '${NON ASCII}' does not exist.
    File Should Be Empty    ${NON ASCII}

File Should Not Be Empty
    [Documentation]    FAIL File '${TESTFILE}' is empty.
    Test File Should Not Be Empty    ${TESTFILE}

Non-ASCII File Should Not Be Empty
    [Documentation]    FAIL File '${NON ASCII}' is empty.
    Test File Should Not Be Empty    ${NON ASCII}

File With Space Should Not Be Empty
    [Documentation]    FAIL File '${WITH SPACE}' is empty.
    Test File Should Not Be Empty    ${WITH SPACE}

File Should Not Be Empty When File Does Not Exist
    [Documentation]    FAIL File '${NON ASCII}' does not exist.
    File Should Not Be Empty    ${NON ASCII}

Path as `pathlib.Path`
    Create Directory                 ${BASE}/dir
    Directory Should Be Empty        ${PATH/'dir'}
    Create File                      ${BASE}/dir/file.txt
    File Should Be Empty             ${PATH/'dir/file.txt'}
    Create File                      ${BASE}/dir/file.txt    content
    File Should Not Be Empty         ${PATH/'dir/file.txt'}
    Directory Should Not Be Empty    ${PATH/'dir'}

*** Keywords ***
Test Directory Should Be Empty
    [Arguments]    ${dir}
    Create Directory    ${dir}
    Directory Should Be Empty    ${dir}    this should not fail
    Create Directory    ${dir}/dir
    Create File    ${dir}/file.txt
    Create File    ${dir}/nöẗ önlÿ äscïï
    Directory Should Be Empty    ${dir}

Test Directory Should Not Be Empty
    [Arguments]    ${dir}
    Create Directory    ${dir}
    Create File    ${dir}/file.txt
    Directory Should Not Be Empty    ${dir}    this should not fail
    Remove File    ${dir}/file.txt
    Directory Should Not Be Empty    ${dir}

Test File Should Be Empty
    [Arguments]    ${file}
    Create File    ${file}
    File Should Be Empty    ${file}    this should not fail
    Create File    ${file}    some content
    File Should Be Empty    ${file}

Test File Should Not Be Empty
    [Arguments]    ${file}
    Create File    ${file}    some content
    File Should Not Be Empty    ${file}    this should not fail
    Create File    ${file}
    File Should Not Be Empty    ${file}

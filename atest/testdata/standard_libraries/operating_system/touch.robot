*** Settings ***
Test Setup      Create Base Test Directory
Suite Teardown  Remove Base Test Directory
Resource        os_resource.robot

*** Test Cases ***
Touch Non-Existing File
    Touch  ${TESTFILE}
    File Should Be Empty  ${TESTFILE}

Touch Existing File
    Create File  ${TESTFILE}  Some text\nin 2 lines\n
    ${time1} =  Get Modified Time  ${TESTFILE}  epoch
    Sleep  2.5 s
    Touch  ${TESTFILE}
    ${time2} =  Get Modified Time  ${TESTFILE}  epoch
    Should Be True  ${time2} > ${time1}
    Touch  ${TESTFILE}
    ${content} =  Get File  ${TESTFILE}
    Should Be Equal  ${content}  Some text\nin 2 lines\n

Touch Non-ASCII File
    Touch  ${NONASCII}
    File Should Be Empty  ${NONASCII}

Touch File With Space
    Touch  ${WITHSPACE}
    File Should Be Empty  ${WITHSPACE}

Touching Directory Fails
    [Documentation]  FAIL Cannot touch '${CURDIR}' because it is a directory
    Touch  ${CURDIR}

Touch When Parent Does Not Exist Fails
    [Documentation]  FAIL Cannot touch '${TESTDIR}${/}file.txt' because its parent directory does not exist
    Fail If Dir Exists  ${TESTDIR}
    Touch  ${TESTDIR}/file.txt

*** Keywords ***
Remove Temps
    Remove File  ${TESTFILE}
    Remove Dir  ${TESTDIR}  recursive


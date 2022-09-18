*** Settings ***
Suite Teardown    Remove Base Test Directory
Test Setup        Create Base Test Directory
Resource          os_resource.robot

*** Test Cases ***
Get File Size
    Create File    ${TESTFILE}
    ${size} =    Get File Size    ${TESTFILE}
    Should Be Equal    ${size}    ${0}
    Create File    ${NON ASCII}    x
    ${size} =    Get File Size    ${NON ASCII}
    Should Be Equal    ${size}    ${1}
    Create File    ${WITH SPACE}    some content
    ${size} =    Get File Size    ${WITH SPACE}
    Should Be Equal    ${size}    ${12}
    ${size} =    Get File Size    ${CURDIR}/get_file_size.robot
    Should Be True    0 < ${size} < 1111

Get size of non-existing file
    [Documentation]    FAIL File '${EXECDIR}${/}non.ex' does not exist.
    Get File Size    non.ex

Get size of directory
    [Documentation]    FAIL File '${CURDIR}' does not exist.
    Get File Size    ${CURDIR}

Path as `pathlib.Path`
    Create File    ${BASE}/file.txt    content
    ${size} =    Get File Size    ${PATH/'file.txt'}
    Should Be Equal    ${size}    ${7}

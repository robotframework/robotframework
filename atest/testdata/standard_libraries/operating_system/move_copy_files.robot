*** Settings ***
Test Setup        Create Test Files For Multi-file Operations
Test Teardown     Remove Base Test Directory
Resource          os_resource.robot

*** Variables ***
${SOURCE}         ${BASE}${/}move_from
${SOURCE2}        ${BASE}${/}move_from_dir1
${SOURCE3}        ${BASE}${/}move_from_dir2
${SOURCE GLOB}    ${BASE}${/}\[move]_from_dir_glob
${GLOB FILE}      foo[bar].txt
${DEST}           ${BASE}${/}move_to

*** Test Cases ***
Move One File With Move Files
    Move Files    ${SOURCE}/movecopy-*.txt    ${DEST}
    Directory Should Have Items    ${DEST}    movecopy-one.txt
    Remove Values From List    ${SOURCE FILES}    movecopy-one.txt
    Directory Should Have Items    ${SOURCE}    @{SOURCE FILES}

Move Files fails when no destination
    [Documentation]    FAIL Must contain destination and at least one source.
    Move Files    ${source}movecopy-*.txt

Move Files without arguments fails
    [Documentation]    FAIL Must contain destination and at least one source.
    Move Files

Move Multiple Files
    Move Files    ${SOURCE}/movecopy_multi-*.txt    ${DEST}
    Directory Should Have Items    ${DEST}
    ...    movecopy_multi-1.txt
    ...    movecopy_multi-2.txt
    Remove Values From List    ${SOURCE FILES}
    ...    movecopy_multi-1.txt
    ...    movecopy_multi-2.txt
    Directory Should Have Items    ${SOURCE}    @{SOURCE FILES}

Move Multiple Files From Multiple Directories
    Move Files    ${BASE}/*dir[12]${/}movecopy_multi_dir-*.txt    ${DEST}
    Directory Should Have Items    ${DEST}
    ...    movecopy_multi_dir-1.txt
    ...    movecopy_multi_dir-2.txt
    ...    movecopy_multi_dir-3.txt
    ...    movecopy_multi_dir-4.txt
    Remove Values From List    ${SOURCE FILES 2}
    ...    movecopy_multi_dir-1.txt
    ...    movecopy_multi_dir-2.txt
    Remove Values From List    ${SOURCE FILES 3}
    ...    movecopy_multi_dir-3.txt
    ...    movecopy_multi_dir-4.txt
    Directory Should Have Items    ${SOURCE2}    @{SOURCE FILES 2}
    Directory Should Have Items    ${SOURCE3}    @{SOURCE FILES 3}

Move List of Files
    Move Files    ${SOURCE}/movecopy_list-1.txt    ${SOURCE}/movecopy_list-2.txt    ${DEST}
    Directory Should Have Items    ${DEST}
    ...    movecopy_list-1.txt
    ...    movecopy_list-2.txt
    Remove Values From List    ${SOURCE FILES}
    ...    movecopy_list-1.txt
    ...    movecopy_list-2.txt
    Directory Should Have Items    ${SOURCE}    @{SOURCE FILES}

Move List of Files with Patterns
    Move Files    ${SOURCE}/movecopy_list-3.txt    ${SOURCE}/movecopy_list-4.txt
    ...    ${SOURCE}/movecopy_list_pattern-*.txt    ${SOURCE}/movecopy_list_pattern2-*.txt
    ...    ${DEST}
    Directory Should Have Items    ${DEST}
    ...    movecopy_list-3.txt
    ...    movecopy_list-4.txt
    ...    movecopy_list_pattern-1.txt
    ...    movecopy_list_pattern-2.txt
    ...    movecopy_list_pattern2-3.txt
    ...    movecopy_list_pattern2-4.txt
    Remove Values From List    ${SOURCE FILES}
    ...    movecopy_list-3.txt
    ...    movecopy_list-4.txt
    ...    movecopy_list_pattern-1.txt
    ...    movecopy_list_pattern-2.txt
    ...    movecopy_list_pattern2-3.txt
    ...    movecopy_list_pattern2-4.txt
    Directory Should Have Items    ${SOURCE}    @{SOURCE FILES}

Moving Non-existing Files
    Move Files    ${SOURCE}/non_existing.txt    ${SOURCE}/non_existing_pattern*.txt    ${DEST}
    Directory Should Be Empty    ${DEST}
    Directory Should Have Items    ${SOURCE}    @{SOURCE FILES}

Copy One File To Dir With Copy Files
    Copy Files    ${SOURCE}/movecopy-*.txt    ${DEST}
    Directory Should Have Items    ${DEST}    movecopy-one.txt
    Directory Should Have Items    ${SOURCE}    @{SOURCE FILES}

Copy Files fails when no destination
    [Documentation]    FAIL Must contain destination and at least one source.
    Copy Files    ${SOURCE}/movecopy-*.txt

Copy Files without arguments fails
    [Documentation]    FAIL Must contain destination and at least one source.
    Copy Files

Copy Files destination can not be an existing file
    [Documentation]    FAIL Destination '${SOURCE}${/}movecopy_list-1.txt' exists and is not a directory.
    Copy Files    ${SOURCE}/movecopy_list-2.txt    ${SOURCE}/movecopy_list-1.txt

Move Files destination can not be an existing file
    [Documentation]    FAIL Destination '${SOURCE}${/}movecopy_list-1.txt' exists and is not a directory.
    Move Files    ${SOURCE}/movecopy_list-2.txt    ${SOURCE}/movecopy_list-1.txt

Copy Files directory will be created if it does not exist
    Copy Files    ${SOURCE}/movecopy_list-1.txt    ${DEST}/copieddir
    Directory Should Have Items    ${DEST}/copieddir    movecopy_list-1.txt

Move Files directory will be created if it does not exist
    Move Files    ${SOURCE}/movecopy_list-1.txt    ${DEST}/moveddir
    Directory Should Have Items    ${DEST}/moveddir    movecopy_list-1.txt

Copy One File To File With Copy Files
    Copy Files    ${SOURCE}/movecopy-*.txt    ${DEST}/copied-movecopy.txt
    Directory Should Have Items    ${DEST}    copied-movecopy.txt
    Directory Should Have Items    ${SOURCE}    @{SOURCE FILES}

Copy Multiple Files
    Copy Files    ${SOURCE}/movecopy_multi-*.txt    ${DEST}
    Directory Should Have Items    ${DEST}    movecopy_multi-1.txt    movecopy_multi-2.txt
    Directory Should Have Items    ${SOURCE}    @{SOURCE FILES}

Copy Multiple Files From Multiple Directories
    Copy Files    ${BASE}/*dir[12]${/}movecopy_multi_dir-*.txt    ${DEST}
    Directory Should Have Items    ${DEST}
    ...    movecopy_multi_dir-1.txt
    ...    movecopy_multi_dir-2.txt
    ...    movecopy_multi_dir-3.txt
    ...    movecopy_multi_dir-4.txt
    Directory Should Have Items    ${SOURCE2}    @{SOURCE FILES 2}
    Directory Should Have Items    ${SOURCE3}    @{SOURCE FILES 3}

Copy List of Files
    Copy Files    ${SOURCE}/movecopy_list-1.txt    ${SOURCE}/movecopy_list-2.txt    ${DEST}
    Directory Should Have Items    ${DEST}
    ...    movecopy_list-1.txt
    ...    movecopy_list-2.txt
    Directory Should Have Items    ${SOURCE}    @{SOURCE FILES}

Copy List of Files with Patterns
    Copy Files    ${SOURCE}/movecopy_list-3.txt
    ...    ${SOURCE}/movecopy_list-4.txt    ${SOURCE}/movecopy_list_pattern-*.txt
    ...    ${SOURCE}/movecopy_list_pattern2-*.txt    ${DEST}
    Directory Should Have Items    ${DEST}
    ...    movecopy_list-3.txt
    ...    movecopy_list-4.txt
    ...    movecopy_list_pattern-1.txt
    ...    movecopy_list_pattern-2.txt
    ...    movecopy_list_pattern2-3.txt
    ...    movecopy_list_pattern2-4.txt
    Directory Should Have Items    ${SOURCE}    @{SOURCE FILES}

Copying Non-existing Files
    Copy Files    ${SOURCE}/non_existing.txt    ${SOURCE}/non_existing_pattern*.txt    ${DEST}
    Directory Should Be Empty    ${DEST}
    Directory Should Have Items    ${SOURCE}    @{SOURCE FILES}

Copying And Moving With backslash in glob pattern
    Copy Files    ${BASE}/move_from//movecopy_list_pattern-*.txt    ${DEST}
    Move Files    ${BASE}/move_from//movecopy_list_pattern2-*.txt    ${DEST}
    Directory Should Have Items    ${DEST}
    ...    movecopy_list_pattern-1.txt
    ...    movecopy_list_pattern-2.txt
    ...    movecopy_list_pattern2-3.txt
    ...    movecopy_list_pattern2-4.txt

Copying From Name With Glob
    Copy Files    ${SOURCE GLOB}/${GLOB FILE}    ${DEST}
    Directory Should Have Items    ${DEST}    ${GLOB FILE}

Moving From Name With Glob
    Move Files    ${SOURCE GLOB}/${GLOB FILE}    ${DEST}
    Directory Should Have Items    ${DEST}    ${GLOB FILE}

Path as `pathlib.Path`
    Move Files    ${{pathlib.Path($SOURCE)/'movecopy-*.txt'}}    ${{pathlib.Path($DEST)}}
    Directory Should Have Items    ${DEST}    movecopy-one.txt
    Remove Values From List    ${SOURCE FILES}    movecopy-one.txt
    Directory Should Have Items    ${SOURCE}    @{SOURCE FILES}
    Copy Files    ${{pathlib.Path($DEST)/'*.txt'}}    ${{pathlib.Path($DEST)/'new'}}
    Directory Should Have Items    ${DEST}/new    movecopy-one.txt
    Directory Should Have Items    ${DEST}    movecopy-one.txt    new

*** Keywords ***
Create Test Files For Multi-file Operations
    Create Directory    ${SOURCE}
    Create Directory    ${SOURCE2}
    Create Directory    ${SOURCE3}
    Create Directory    ${SOURCE GLOB}
    Create Directory    ${DEST}
    Set Test Variable    @{SOURCE FILES}
    ...    movecopy-one.txt
    ...    movecopy_list-1.txt
    ...    movecopy_list-2.txt
    ...    movecopy_list-3.txt
    ...    movecopy_list-4.txt
    ...    movecopy_list_pattern-1.txt
    ...    movecopy_list_pattern-2.txt
    ...    movecopy_list_pattern2-3.txt
    ...    movecopy_list_pattern2-4.txt
    ...    movecopy_multi-1.txt
    ...    movecopy_multi-2.txt
    ...    rename-one.txt
    ...    rename_list_pattern3-5.txt
    ...    rename_list_pattern3-6.txt
    ...    rename_list_pattern4-7.txt
    ...    rename_list_pattern4-8.txt
    ...    rename_multi-1.txt
    ...    rename_multi-2.txt
    Set Test Variable    @{SOURCE FILES 2}
    ...    movecopy_multi_dir-1.txt
    ...    movecopy_multi_dir-2.txt
    Set Test Variable    @{SOURCE FILES 3}
    ...    movecopy_multi_dir-3.txt
    ...    movecopy_multi_dir-4.txt
    # All the files possibly used in the test are created
    FOR    ${file}    IN    @{SOURCE FILES}
        Create File    ${SOURCE}/${file}
    END
    FOR    ${file}    IN    @{SOURCE FILES 2}
        Create File    ${SOURCE2}/${file}
    END
    FOR    ${file}    IN    @{SOURCE FILES 3}
        Create File    ${SOURCE3}/${file}
    END
    Create File    ${SOURCE GLOB}/${GLOB FILE}

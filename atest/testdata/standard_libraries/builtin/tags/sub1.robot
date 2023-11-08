*** Settings ***
Suite Setup       Set And Remove Tags
Force Tags        force-remove-please    force
Default Tags      default-remove-also    default
Library           Collections

*** Variables ***
@{SUITE_TAGS}     default    force    force-init    set    set-init

*** Test Cases ***
Set And Remove Tags In Suite Level
    Should Be Equal    ${TEST_TAGS}    ${SUITE_TAGS}

Set No Tags
    Set Tags
    Should Be Equal    ${TEST_TAGS}    ${SUITE_TAGS}

Set One Tag
    Set Tags    one
    Tags Should Be Added    one

Set Multiple Tags
    Set Tags    1    2    3
    Set Tags    HELLO    \    Some spaces here
    Tags Should Be Added    1    2    3    HELLO    Some spaces here

Tags Set In One Test Are Not Visible To Others
    Should Be Equal    ${TEST_TAGS}    ${SUITE_TAGS}

Remove No Tags
    Remove Tags
    Should Be Equal    ${TEST_TAGS}    ${SUITE_TAGS}

Remove One Tag
    Remove Tags    force
    Tags Should Be Removed    force

Remove Non-Existing Tag
    Remove Tags    non-existing
    Should Be Equal    ${TEST_TAGS}    ${SUITE_TAGS}

Remove Multiple Tags
    Remove Tags    default    SET    non-existing
    Remove Tags    \    set-init
    Tags Should Be Removed    default    set    set-init

Remove Tags With Pattern
    Remove Tags    ???
    Tags Should Be Removed    set
    Remove Tags    *-init    DEF*    non-existing-*
    Tags Should Be Removed    set    force-init    set-init    default
    Remove Tags    *
    Should Be True    ${TEST_TAGS} == []

Tags Removed In One Test Are Not Removed From Others
    Should Be Equal    ${TEST_TAGS}    ${SUITE_TAGS}

Set And Remove Tags In A User Keyword
    Remove Tags    *
    Set Tags    tc    tc-2
    Should Be True    ${TEST_TAGS} == ['tc','tc-2']
    Set And Remove Tags In UK
    Should Be True    ${TEST_TAGS} == ['tc','uk','uk2']

*** Keywords ***
Set And Remove Tags
    Set Tags    set    set-REMOVE-this    take this out too
    Remove Tags    non-existing    *-remove-*    Take this out TOO

Tags Should Be Added
    [Arguments]    @{added}
    ${tags} =    Combine Lists    ${SUITE_TAGS}    ${added}
    Sort List    ${tags}
    Sort List    ${TEST_TAGS}
    Should Be Equal    ${TEST_TAGS}    ${tags}

Tags Should Be Removed
    [Arguments]    @{removed}
    ${tags} =    Copy List    ${SUITE_TAGS}
    Remove Values From List    ${tags}    @{removed}
    Should Be Equal    ${TEST_TAGS}    ${tags}

Set And Remove Tags In UK
    Should Be True    ${TEST_TAGS} == ['tc','tc-2']
    Set Tags    uk    uk-2    remove-asap
    Remove Tags    ??-2    remove-asap
    Should Be True    ${TEST_TAGS} == ['tc','uk']
    Set And Remove Tags In UK 2
    Should Be True    ${TEST_TAGS} == ['tc','uk','uk2']

Set And Remove Tags In UK 2
    Should Be True    ${TEST_TAGS} == ['tc','uk']
    Set Tags    \    remove-me    uk2
    Remove Tags    ??????-??
    Should Be True    ${TEST_TAGS} == ['tc','uk','uk2']

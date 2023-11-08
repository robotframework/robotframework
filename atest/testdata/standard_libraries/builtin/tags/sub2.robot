*** Settings ***
Suite Teardown    Set Tags    this-should-fail
Library           Collections

*** Variables ***
${ERROR}    FAIL Parent suite teardown failed:\n'Set Tags' cannot be used in suite teardown.

*** Test Cases ***
Set Tags In Test Setup
    [Documentation]    ${ERROR}
    [Tags]    tag
    [Setup]    Set And Remove Tags    setup
    Should Be True    ${TEST_TAGS} == ['set-init','setup','tag']

Set Tags In Test Teardown
    [Documentation]    ${ERROR}
    No Operation
    [Teardown]    Set And Remove Tags    teardown

Modifying ${TEST TAGS} after setting them has no affect on tags test has
    [Documentation]    Variable is changed but "real" tags are not. ${ERROR}
    Set Tags    new
    Append To List    ${TEST TAGS}    not really added
    Should Be True    ${TEST TAGS} == ['force-init', 'new', 'set-init', 'not really added']

Modifying ${TEST TAGS} after removing them has no affect on tags test has
    [Documentation]    Variable is changed but "real" tags are not. ${ERROR}
    Remove Tags    *-init
    Append To List    ${TEST TAGS}    not really added
    Should Be True    ${TEST TAGS} == ['not really added']

*** Keywords ***
Set And Remove Tags
    [Arguments]    @{set}
    Set Tags    @{set}
    Remove Tags    force-init
    Log Many    @{TEST_TAGS}

*** Settings ***
Suite Setup     Run Tests  ${EMPTY}    standard_libraries/builtin/tags
Resource        atest_resource.robot

*** Variables ***
@{SUITE_TAGS}  default  force  force-init  set  set-init

*** Test Cases ***
Set And Remove Tags In Suite Level
    Should Have Only Suite Tags  Set And Remove Tags In Suite Level

Set No Tags
    Should Have Only Suite Tags  Set No Tags

Set One Tag
    ${tc} =  Tags Should Have Been Added  Set One Tag  one
    Check Log Message  ${tc.kws[0].msgs[0]}  Set tag 'one'.

Set Multiple Tags
    ${tc} =  Tags Should Have Been Added  Set Multiple Tags  1  2  3  HELLO  Some spaces here
    Check Log Message  ${tc.kws[0].msgs[0]}  Set tags '1', '2' and '3'.
    Check Log Message  ${tc.kws[1].msgs[0]}  Set tags 'HELLO', '' and 'Some spaces here'.

Tags Set In One Test Are Not Visible To Others
    Should Have Only Suite Tags  Tags Set In One Test Are Not Visible To Others

Remove No Tags
    Should Have Only Suite Tags  Remove No Tags

Remove One Tag
    ${tc} =  Tags Should Have Been Removed  Remove One Tag  force
    Check Log Message  ${tc.kws[0].msgs[0]}  Removed tag 'force'.

Remove Non-Existing Tag
    Should Have Only Suite Tags  Remove Non-Existing Tag

Remove Multiple Tags
    ${tc} =  Tags Should Have Been Removed  Remove Multiple Tags  default  set  set-init
    Check Log Message  ${tc.kws[0].msgs[0]}  Removed tags 'default', 'SET' and 'non-existing'.
    Check Log Message  ${tc.kws[1].msgs[0]}  Removed tags '' and 'set-init'.

Remove Tags With Pattern
    Check Test Tags  Remove Tags With Pattern

Tags Removed In One Test Are Not Removed From Others
    Should Have Only Suite Tags  Tags Removed In One Test Are Not Removed From Others

Set And Remove Tags In A User Keyword
    Check Test Tags  Set And Remove Tags In A User Keyword  tc  uk  uk2

Set Tags In Test Setup
    Check Test Tags  Set Tags In Test Setup  set-init  setup  tag

Set Tags In Test Teardown
    Check Test Tags  Set Tags In Test Teardown  set-init  teardown

Using Set And Remove Tags In Suite Teardown Fails
    Should Be Equal  ${SUITE.suites[1].message}  Suite teardown failed:\n'Set Tags' cannot be used in suite teardown.

Modifying ${TEST TAGS} after setting them has no affect on tags test has
    Check Test Tags    ${TEST NAME}    force-init    set-init    new

Modifying ${TEST TAGS} after removing them has no affect on tags test has
    Check Test Tags    ${TEST NAME}

*** Keywords ***
Should Have Only Suite Tags
    [Arguments]  ${testname}
    Check Test Tags  ${testname}  @{SUITE_TAGS}

Tags Should Have Been Added
    [Arguments]  ${testname}  @{added}
    @{tags} =  Create List  @{SUITE_TAGS}  @{added}
    Sort List  ${tags}
    ${tc} =  Check Test Tags  ${testname}  @{tags}
    RETURN  ${tc}

Tags Should Have Been Removed
    [Arguments]  ${testname}  @{removed}
    @{tags} =  Copy List  ${SUITE_TAGS}
    Remove Values From List  ${tags}  @{removed}
    ${tc} =  Check Test Tags  ${testname}  @{tags}
    RETURN  ${tc}

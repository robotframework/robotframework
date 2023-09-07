*** Settings ***
Suite Setup       Check Variables In Suite Setup    Automatic Variables.Auto2
...               ${EMPTY}    {}    @{PREV_TEST}
Suite Teardown    Check Variables In Suite Teardown    Automatic Variables.Auto2    FAIL
...               1 test, 0 passed, 1 failed
...               @{LAST_TEST}
Force Tags        include this test
Resource          resource.robot

*** Variables ***
@{PREV_TEST}      \&{OPTIONS}    PASS
@{LAST_TEST}      Previous Test Variables Should Have Default Values From Previous Suite    FAIL    Expected failure

*** Test Cases ***
Previous Test Variables Should Have Default Values From Previous Suite
    [Documentation]    FAIL Expected failure
    Check Previous Test Variables    @{PREV_TEST}
    Fail    Expected failure

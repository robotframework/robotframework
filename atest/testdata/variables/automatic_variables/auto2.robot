*** Setting ***
Suite Setup       Check Variables In Suite Setup    Automatic Variables.Auto2
...               ${EMPTY}    {}    @{PREV_TEST}
Suite Teardown    Check Variables In Suite Teardown    Automatic Variables.Auto2    FAIL
...               1 test, 0 passed, 1 failed
...               @{LAST_TEST}
Resource          resource.robot

*** Variable ***
@{PREV_TEST}      Previous Test Variables Should Have Correct Values When That Test Fails    PASS
@{LAST_TEST}      Previous Test Variables Should Have Default Values From Previous Suite    FAIL    Expected failure

*** Test Case ***
Previous Test Variables Should Have Default Values From Previous Suite
    [Documentation]    FAIL Expected failure
    Check Previous Test Variables    @{PREV_TEST}
    Fail    Expected failure

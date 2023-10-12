*** Settings ***
Suite Setup       Fail    Expected failure
Suite Teardown    Log    Suite teardown executed

*** Test Cases ***
Test 1
    [Documentation]    FAIL Parent suite setup failed:\nExpected failure
    Fail    This is not executed

Test 2
    [Documentation]    FAIL Parent suite setup failed:\nExpected failure
    Fail    This is not executed

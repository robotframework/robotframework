*** Settings ***
Suite Teardown    Fail    Expected failure

*** Test Cases ***
Test passed but suite teardown fails
    [Documentation]    FAIL Parent suite teardown failed:\nExpected failure
    No Operation

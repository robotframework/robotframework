*** Settings ***
Suite Teardown    No Operation

*** Test Cases ***
Failing with tag
    [Tags]    excluded_tag
    Fail    failed test

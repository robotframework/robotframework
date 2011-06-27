*** Settings ***
Suite Setup     Log  suite setup
Suite Teardown  Log  suite teardown

*** Test Cases ***
Test
    [Setup]  Log  test setup
    Keyword with teardown
    [Teardown]  Log  test teardown

*** Keywords ***
Keyword with teardown
    No Operation
    [Teardown]  Log  keyword teardown


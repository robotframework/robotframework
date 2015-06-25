*** Settings ***
Library  Exceptions
Suite Teardown  Log  Suite Teardown

*** Test Cases ***
Exit From Python Keyword
    [Documentation]  FAIL  FatalCatastrophyException
    [Teardown]  Log  This should be executed
    [Tags]    some tag
    Exit On Failure

Test That Should Not Be Run 1
    [Documentation]  FAIL  Test execution stopped due to a fatal error.
    Fail  This should not be executed

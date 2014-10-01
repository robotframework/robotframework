*** Settings ***
Library  Exceptions
Suite Setup  Exit On Failure
Suite Teardown  Log  Tearing down 1

*** Test Cases ***
Test That Should Not Be Run 1
    [Documentation]  FAIL  Test execution stopped due to a fatal error.
    Fail  This should not be executed

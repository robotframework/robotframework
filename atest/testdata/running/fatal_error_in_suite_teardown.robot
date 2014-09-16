*** Settings ***
Library  Exceptions
Suite Teardown  Suite Teardown With Fatal Error

*** Test Cases ***
Test
    No Operation

*** Keywords ***
Suite Teardown With Fatal Error
    Exit On Failure
    Log  This Should Not Be executed

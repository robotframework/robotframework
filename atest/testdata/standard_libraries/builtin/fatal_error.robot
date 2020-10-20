*** Settings ***
Suite Teardown    Fatal Error

*** Test Cases ***
Test is stopped when `Fatal Error` keyword is used
    [Documentation]    FAIL
    ...    Faster, Pussycat! Kill! Kill!
    ...
    ...    Also parent suite teardown failed:
    ...    AssertionError
    Fatal Error    Faster, Pussycat! Kill! Kill!
    Fail    This isn't executed anymore

Subsequent tests are not executed after `Fatal Error` keyword has been used
    [Documentation]    FAIL
    ...    Test execution stopped due to a fatal error.
    ...
    ...    Also parent suite teardown failed:
    ...    AssertionError
    Fail    This isn't executed anymore

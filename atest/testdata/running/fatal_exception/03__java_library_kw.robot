*** Settings ***
Library  JavaExceptions

*** Test Cases ***
Exit From Java Keyword
    [Documentation]  FAIL  FatalCatastrophyException
    Throw Exit On Failure

Test That Should Not Be Run 3
    [Documentation]  FAIL  Test execution stopped due to a fatal error.
    [Tags]    foo
    Fail  This should not be executed

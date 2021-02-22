*** Settings ***
Library           Exceptions

*** Test Cases ***
robot.api.FatalError
    [Documentation]    FAIL FatalError: BANG!
    Exit on failure    standard=True
    Fail    Should not be executed

Test That Should Not Be Run
    [Documentation]    FAIL Test execution stopped due to a fatal error.
    Fail    Should not be executed

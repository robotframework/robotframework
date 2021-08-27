*** Settings ***
Library           Exceptions

*** Test Cases ***
robot.api.FatalError
    [Documentation]    FAIL *HTML* FatalError: Big <b>BANG</b>!
    Exit on failure    Big <b>BANG</b>!    html=True    standard=True
    Fail    Should not be executed

Test That Should Not Be Run
    [Documentation]    FAIL Test execution stopped due to a fatal error.
    Fail    Should not be executed

*** Settings ***
Suite Teardown    My Teardown    Teardown of    sub test suite directory
Test Setup        Log    Default setup from sub suite file
Force Tags        sub suite force
Test Timeout      1 minute 52 seconds
Library           OperatingSystem
Megadata          This causes recommendation.

*** Variables ***
${default}        default

*** Keywords ***
My Teardown
    [Arguments]    @{msg_parts}
    ${msg}    Create Message    @{msg_parts}
    Log    ${msg}
    Directory Should Not Be Empty    ${CURDIR}    Test that OS lib was imported

Create Message
    [Arguments]    @{msg_parts}
    ${msg}    Catenate    @{msg_parts}
    RETURN    ${msg}

*** Settings ***
Documentation     Setting metadata for test suite directory
Suite Setup       My Setup    Setup of test suite directory
Suite Teardown    My Teardown    Teardown of    test suite directory
Test Setup        Log    Default setup from suite file    # Keywords and variables used    here should exist in namespace
Test Teardown     Log    Default teardown from suite file    # where setup/teardown are    used
Force Tags        suite force
Test Timeout      13 days 6 hours 50 minutes
Library           OperatingSystem
Invalid
Default Tags      Not allowed
Test Template     Not allowed

*** Variables ***
${default}        default
${default_tag_2}    suite${default}2

*** Keywords ***
My Setup
    [Arguments]    ${msg}
    Log    ${msg}

My Teardown
    [Arguments]    @{msg_parts}
    ${msg} =    Create Message    @{msg_parts}
    Log    ${msg}
    Directory Should Not Be Empty    ${CURDIR}    Test that OS lib was imported

Create Message
    [Arguments]    @{msg_parts}
    ${msg} =    Catenate    @{msg_parts}
    RETURN    ${msg}


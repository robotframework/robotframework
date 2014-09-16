*** Setting ***
Suite Teardown    My Teardown    Teardown of    sub test suite directory
Test Setup        Log    Default setup from sub suite file
Force Tags        sub suite force
Test Timeout      1 minute 52 seconds
Library           OperatingSystem
Invalid In Sub

*** Variable ***
${default}        default

*** Keyword ***
My Teardown
    [Arguments]    @{msg_parts}
    ${msg}    Create Message    @{msg_parts}
    Log    ${msg}
    Fail If Dir Empty    ${CURDIR}    Test that OS lib was imported

Create Message
    [Arguments]    @{msg_parts}
    ${msg}    Catenate    @{msg_parts}
    [Return]    ${msg}


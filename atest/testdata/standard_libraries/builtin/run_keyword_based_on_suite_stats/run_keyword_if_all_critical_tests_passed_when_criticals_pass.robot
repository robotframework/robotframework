*** Settings ***
Suite Teardown    Run Keyword If All Critical Tests Passed    My Teardown
Default Tags      critical

*** Variables ***
${MESSAGE}        Suite teardown message

*** Test Cases ***
Passing Critical Test
    No Operation

Another Passing Critical Test
    Comment    Hello, world

Failing non-critical Test
    [Tags]    non-critical
    Fail

*** Keywords ***
My Teardown
    Log    ${MESSAGE}

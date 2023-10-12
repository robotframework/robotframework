*** Settings ***
Suite Teardown    Run Keyword If All Tests Passed    My Teardown
Default Tags      critical

*** Variables ***
${MESSAGE}        Suite teardown message

*** Test Cases ***
Passing Critical
    No Operation

Passing Non-critical
    [Tags]    non-critical
    No Operation

*** Keywords ***
My Teardown
    Log    ${MESSAGE}

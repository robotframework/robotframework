*** Settings ***
Suite Teardown    Run Keyword If Any Critical Tests Failed    My Teardown
Default Tags      critical

*** Variables ***
${MESSAGE}        Suite teardown message

*** Test Cases ***
Failing Critical test
    Fail    Expected failure

*** Keywords ***
My Teardown
    Log    ${MESSAGE}

*** Settings ***
Suite Teardown    Run Keyword If Any Tests Failed    My Teardown

*** Variables ***
${MESSAGE}        Suite teardown message

*** Test Cases ***
Failing Non Critical test
    Fail    Expected failure

*** Keywords ***
My Teardown
    Log    ${MESSAGE}

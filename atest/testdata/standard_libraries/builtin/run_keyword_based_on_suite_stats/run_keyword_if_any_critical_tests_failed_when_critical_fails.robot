*** Setting ***
Suite Teardown    Run Keyword If Any Critical Tests Failed    My Teardown
Default Tags      critical

*** Variable ***
${MESSAGE}        Suite teardown message

*** Test Case ***
Failing Critical test
    Fail    Expected failure

*** Keyword ***
My Teardown
    Log    ${MESSAGE}

*** Setting ***
Suite Teardown    Run Keyword If Any Tests Failed    My Teardown

*** Variable ***
${MESSAGE}        Suite teardown message

*** Test Case ***
Failing Non Critical test
    Fail    Expected failure

*** Keyword ***
My Teardown
    Log    ${MESSAGE}

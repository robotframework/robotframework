*** Setting ***
Suite Teardown    Run Keyword If All Tests Passed    My Teardown
Default Tags      critical

*** Variable ***
${MESSAGE}        Suite teardown message

*** Test Case ***
Passing Critical
    Noop

Passing Non-critical
    [Tags]    non-critical
    Noop

*** Keyword ***
My Teardown
    Log    ${MESSAGE}

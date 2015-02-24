*** Setting ***
Suite Teardown    Run Keyword If All Tests Passed    My Teardown
Default Tags      critical

*** Variable ***
${MESSAGE}        Suite teardown message

*** Test Case ***
Passing Critical
    No Operation

Passing Non-critical
    [Tags]    non-critical
    No Operation

*** Keyword ***
My Teardown
    Log    ${MESSAGE}

*** Setting ***
Suite Teardown    Run Keyword If All Critical Tests Passed    My Teardown
Default Tags      critical

*** Variable ***
${MESSAGE}        Suite teardown message

*** Test Case ***
Passing Critical Test
    No Operation

Another Passing Critical Test
    Comment    Hello, world

Failing non-critical Test
    [Tags]    non-critical
    Fail

*** Keyword ***
My Teardown
    Log    ${MESSAGE}

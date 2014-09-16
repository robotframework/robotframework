*** Setting ***
Suite Setup       Log    Setup of test case file
Suite Teardown    Log    Teardown of test case file
Test Setup        Log    Default setup from test file
Test Teardown     Log    Default teardown from test file
Force Tags        test force
Default Tags      test default
Test Timeout      7 hour 8 minutes 9 seconds

*** Test Case ***
S2TC1 No metadata
    NOOP

S2TC1 Tags
    [Tags]    test tag 1    test tag 2    test tag 3
    NOOP

S2TC1 Fixture
    [Setup]    Log    Setup defined in test
    NOOP
    [Teardown]    Log    Teardown defined in test

S2TC1 Timeout
    [Documentation]    FAIL Test timeout 1 second exceeded.
    [Timeout]    1 s
    Sleep    1.1

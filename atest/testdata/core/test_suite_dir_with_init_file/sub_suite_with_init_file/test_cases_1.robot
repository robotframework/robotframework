*** Setting ***
Suite Setup       Log    Setup of test case file
Suite Teardown    Log    Teardown of test case file
Test Setup        Log    Default setup from test file
Test Teardown     Log    Default teardown from test file
Force Tags        test force
Default Tags      test default
Test Timeout      4 h 5 m 6 s

*** Test Case ***
S1TC1 No metadata
    NOOP

S1TC1 Tags
    [Tags]    test tag 1    test tag 2
    NOOP

S1TC1 Fixture
    [Setup]    Log    Setup defined in test
    NOOP
    [Teardown]    Log    Teardown defined in test

S1TC1 Timeout
    [Documentation]    FAIL Test timeout 1 second exceeded.
    [Timeout]    1 s
    Sleep    1.1

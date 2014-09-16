*** Setting ***
Suite Setup       Log    Setup of test case file
Suite Teardown    Log    Teardown of test case file
Test Setup        Log    Default setup from test file
Test Teardown     Log    Default teardown from test file
Force Tags        test force    suite force    # dublicate should be ignored
Default Tags      test default
Test Timeout      1 hour 2 minutes 3 seconds

*** Test Case ***
TC1 No metadata
    NOOP

TC1 Tags
    [Tags]    test tag 1    test tag 2
    NOOP

TC1 Fixture
    [Setup]    Log    Setup defined in test
    NOOP
    [Teardown]    Log    Teardown defined in test

TC1 Timeout
    [Documentation]    FAIL Test timeout 1 second exceeded.
    [Timeout]    1 s
    Sleep    1.1

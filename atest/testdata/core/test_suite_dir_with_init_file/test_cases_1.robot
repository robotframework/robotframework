*** Settings ***
Suite Setup       Log    Setup of test case file
Suite Teardown    Log    Teardown of test case file
Test Setup        Log    Default setup from test file
Test Teardown     Log    Default teardown from test file
Force Tags        test force    suite force    # dublicate should be ignored
Default Tags      test default
Test Timeout      1 hour 2 minutes 3 seconds

*** Test Cases ***
TC1 No metadata
    No Operation

TC1 Tags
    [Tags]    test tag 1    test tag 2
    No Operation

TC1 Fixture
    [Setup]    Log    Setup defined in test
    No Operation
    [Teardown]    Log    Teardown defined in test

TC1 Timeout
    [Documentation]    FAIL Test timeout 100 milliseconds exceeded.
    [Timeout]    0.1s
    Sleep    1s

*** Settings ***
Suite Setup       Log    Setup of test case file
Suite Teardown    Log    Teardown of test case file
Test Setup        Log    Default setup from test file
Test Teardown     Log    Default teardown from test file
Force Tags        test force
Default Tags      test default
Test Timeout      4 h 5 m 6 s

*** Test Cases ***
S1TC1 No metadata
    No Operation

S1TC1 Tags
    [Tags]    test tag 1    test tag 2
    No Operation

S1TC1 Fixture
    [Setup]    Log    Setup defined in test
    No Operation
    [Teardown]    Log    Teardown defined in test

S1TC1 Timeout
    [Documentation]    FAIL Test timeout 101 milliseconds exceeded.
    [Timeout]    101ms
    Sleep    1s

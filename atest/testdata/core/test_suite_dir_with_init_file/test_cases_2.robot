*** Test Case ***
TC2 No Metadata
    Log    Whatever

TC2 Tags
    [Tags]
    NOOP

TC2 Fixture
    [Setup]    Log    Setup defined in test
    NOOP
    [Teardown]    Log    Teardown defined in test

TC2 Timeout
    [Timeout]    1 hour
    Sleep    1.1

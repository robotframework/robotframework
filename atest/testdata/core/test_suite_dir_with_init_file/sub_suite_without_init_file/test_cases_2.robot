*** Test Case ***
S2TC2 No Metadata
    Log    Whatever

S2TC2 Tags
    [Tags]
    NOOP

S2TC2 Fixture
    [Setup]    Log    Setup defined in test
    NOOP
    [Teardown]    Log    Teardown defined in test

S2TC2 Timeout
    [Timeout]    1 day
    Sleep    1.1

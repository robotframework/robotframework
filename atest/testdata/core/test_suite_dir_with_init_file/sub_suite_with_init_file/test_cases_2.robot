*** Test Case ***
S1TC2 No Metadata
    Log    Whatever

S1TC2 Tags
    [Tags]    t1    t2    t3    t4    t5
    NOOP

S1TC2 Fixture
    [Setup]    Log    Setup defined in test
    NOOP
    [Teardown]    Log    Teardown defined in test

S1TC2 Timeout
    [Timeout]    24 hours
    Sleep    1.1

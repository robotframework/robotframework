*** Test Cases ***
S2TC2 No Metadata
    Log    Whatever

S2TC2 Tags
    [Tags]
    No Operation

S2TC2 Fixture
    [Setup]    Log    Setup defined in test
    No Operation
    [Teardown]    Log    Teardown defined in test

S2TC2 Timeout
    [Timeout]    1 day
    Sleep    0.1

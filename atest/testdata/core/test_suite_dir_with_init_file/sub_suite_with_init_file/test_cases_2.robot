*** Test Cases ***
S1TC2 No Metadata
    Log    Whatever

S1TC2 Tags
    [Tags]    t1    t2    t3    t4    t5
    No Operation

S1TC2 Fixture
    [Setup]    Log    Setup defined in test
    No Operation
    [Teardown]    Log    Teardown defined in test

S1TC2 Timeout
    [Timeout]    24 hours
    Sleep    0.1

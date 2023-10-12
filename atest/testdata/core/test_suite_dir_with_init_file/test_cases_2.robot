*** Test Cases ***
TC2 No Metadata
    Log    Whatever

TC2 Tags
    [Tags]
    No Operation

TC2 Fixture
    [Setup]    Log    Setup defined in test
    No Operation
    [Teardown]    Log    Teardown defined in test

TC2 Timeout
    [Timeout]    1 hour
    Sleep    0.1

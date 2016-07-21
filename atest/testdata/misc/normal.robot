*** Setting ***
Documentation     Normal test cases
Force Tags        f1
Default Tags      d1    d_2
Metadata          Something    My Value

*** Test Case ***
First One
    [Tags]    t1    t2
    Log    Test 1
    Log    Logging with debug level    DEBUG
    logs on trace

Second One
    [Documentation]    Nothing interesting here
    [Timeout]    1 day
    Log    Test 2
    Sleep    0.01    # Make sure elapsed time > 0

*** Keyword ***
logs on trace
    [Timeout]    1 hour
    [Tags]    kw    tags
    Log    Log on ${TEST NAME}    TRACE

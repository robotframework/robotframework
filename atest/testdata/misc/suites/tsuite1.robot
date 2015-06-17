*** Setting ***
Documentation     Normal test cases
Force Tags        f1
Default Tags      d1    d2
Metadata          Something    My Value

*** Test Case ***
Suite1 First
    [Tags]    t1
    Log    Suite1_First
    Sleep    0.01    Make sure elapsed time > 0

Suite1 Second
    [Tags]    t2
    Log    Suite1_Second

Third In Suite1
    Log    Suite2_third

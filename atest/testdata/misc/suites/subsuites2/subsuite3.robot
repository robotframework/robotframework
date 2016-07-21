*** Setting ***
Documentation     Normal test cases
Force Tags        f1
Default Tags      d1    d2
Metadata          Something    My Value

*** Test Case ***
SubSuite3 First
    [Tags]    t1    sub3
    Log    SubSuite3_First
    Sleep    0.01    Make sure elapsed time > 0

SubSuite3 Second
    [Tags]    t2    sub3
    Log    SubSuite3_Second

*** Settings ***
Documentation     Normal test cases
Test Tags         f1
Metadata          Something    My Value

*** Test Cases ***
Suite1 First
    [Tags]    t1
    Log    Suite1_First
    Sleep    0.001    Make sure elapsed time > 0

Suite1 Second
    [Tags]    t2
    Log    Suite1_Second

Third In Suite1
    [Tags]    d1    d2
    Log    Suite2_third

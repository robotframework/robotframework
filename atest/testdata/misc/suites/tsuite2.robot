*** Settings ***
Documentation     Normal test cases
Test Tags         f1
Metadata          Something    My Value

*** Test Cases ***
Suite2 First
    [Tags]    t1
    Log    Suite2_First
    Sleep    0.001    Make sure elapsed time > 0

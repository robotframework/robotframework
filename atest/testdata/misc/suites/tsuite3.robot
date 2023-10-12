*** Settings ***
Documentation     Normal test cases
Suite Teardown    Log    Suite Teardown of Tsuite3
Test Tags         f1
Metadata          Something    My Value

*** Test Cases ***
Suite3 First
    [Tags]    t1
    Log    Suite3_First
    Sleep    0.001    Make sure elapsed time > 0

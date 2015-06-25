*** Setting ***
Documentation     Normal test cases
Suite Teardown    Log    Suite Teardonw of Fourth
Force Tags        f1
Default Tags      d1    d2
Metadata          Something    My Value

*** Test Case ***
Suite4 First
    [Documentation]    FAIL Expected
    [Tags]    t1
    Log    Suite4_First
    Sleep    0.01    Make sure elapsed time > 0
    Fail    Expected
    [Teardown]    Log    Huhuu

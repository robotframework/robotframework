*** Setting ***
Documentation     Normal test cases
Suite Setup       Log    ${SETUP MSG}
Suite Teardown    Log    ${TEARDOWN MSG}
Force Tags        f1
Default Tags      d1    d2
Metadata          Something    My Value

*** Variables ***
${SETUP MSG}     Suite Setup of Fourth
${TEARDOWN MSG}  Suite Teardown of Fourth

*** Test Case ***
Suite4 First
    [Documentation]    FAIL Expected
    [Tags]    t1
    Log    Suite4_First
    Sleep    0.01    Make sure elapsed time > 0
    Fail    Expected
    [Teardown]    Log    Huhuu

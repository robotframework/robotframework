*** Settings ***
Documentation     Normal test cases
Suite Setup       Log    ${SETUP MSG}
Suite Teardown    Log    ${TEARDOWN MSG}
Test Tags         f1
Metadata          Something    My Value

*** Variables ***
${SETUP MSG}     Suite Setup of Fourth
${TEARDOWN MSG}  Suite Teardown of Fourth

*** Test Cases ***
Suite4 First
    [Documentation]    FAIL Expected
    [Tags]    t1
    Log    Suite4_First
    Sleep    0.001    Make sure elapsed time > 0
    Fail    Expected
    [Teardown]    Log    Huhuu

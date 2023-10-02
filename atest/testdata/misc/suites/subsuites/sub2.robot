*** Settings ***
Documentation     Normal test cases
Force Tags        f1
Default Tags      d1    d2
Metadata          Something    My Value

*** Variables ***
${SLEEP}          0.001

*** Test Cases ***
SubSuite2 First
    [Tags]
    Log    SubSuite2_First
    Sleep    ${SLEEP}    Make sure elapsed time > 0

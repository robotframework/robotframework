*** Setting ***
Documentation     Normal test cases
Force Tags        f1
Default Tags      d1    d2
Metadata          Something    My Value

*** Variable ***
${SLEEP}          0.1

*** Test Case ***
SubSuite2 First
    [Tags]
    Log    SubSuite2_First
    Sleep    ${SLEEP}    Make sure elapsed time > 0

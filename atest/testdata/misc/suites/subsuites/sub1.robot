*** Setting ***
Documentation     Normal test cases
Force Tags        f1
Default Tags      d1    d2
Metadata          Something    My Value
Suite Setup       ${SETUP}
Suite Teardown    ${TEARDOWN}

*** Variable ***
${SLEEP}          0.1
${FAIL}           NO
${MESSAGE}        Original message
${LEVEL}          INFO
${SETUP}          Setup
${TEARDOWN}       No Operation

*** Test Case ***
SubSuite1 First
    [Tags]    t1
    Log    ${MESSAGE}    ${LEVEL}
    Sleep    ${SLEEP}    Make sure elapsed time > 0
    Should Be Equal    ${FAIL}    NO    This test was doomed to fail

*** Keywords ***
Setup
    Log    Hello, world!

*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    keywords/user_keyword_defined_multiple_times.robot
Force Tags       regression    pybot    jybot
Resource         atest_resource.robot

*** Test Cases ***
Using keyword defined twice fails
    Check Test Case    ${TESTNAME}

Using keyword defined thrice fails as well
    Check Test Case    ${TESTNAME}

Defining keyword multiple times does not cause error
    Should Be Empty    ${ERRORS}

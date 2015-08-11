*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    keywords/user_keyword_defined_multiple_times.robot
Force Tags       regression    pybot    jybot
Resource         atest_resource.robot

*** Test Cases ***
Using keyword defined twice fails
    Check Test Case    ${TESTNAME}
    Creating keyword should have failed    0    Defined Twice

Using keyword defined thrice fails as well
    Check Test Case    ${TESTNAME}
    Creating keyword should have failed    1    Defined Thrice
    Creating keyword should have failed    2    DEFINED THRICE

Keyword with embedded arguments defined twice
    Check Test Case    ${TESTNAME}: Called with embedded args
    Check Test Case    ${TESTNAME}: Called with exact name
    Length Should Be    ${ERRORS}    3

*** Keywords ***
Creating keyword should have failed
    [Arguments]    ${index}    ${name}
    Check Log Message    ${ERRORS[${index}]}
    ...    Creating user keyword '${name}' failed: Keyword with same name defined multiple times.
    ...    ERROR

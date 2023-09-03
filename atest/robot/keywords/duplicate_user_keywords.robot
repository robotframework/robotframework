*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    keywords/duplicate_user_keywords.robot
Resource         atest_resource.robot

*** Test Cases ***
Using keyword defined twice fails
    Check Test Case    ${TESTNAME}
    Creating keyword should have failed    0    Defined Twice    45

Using keyword defined thrice fails as well
    Check Test Case    ${TESTNAME}
    Creating keyword should have failed    1    Defined Thrice    51
    Creating keyword should have failed    2    DEFINED THRICE    54

Keyword with embedded arguments defined twice fails at run-time
    Check Test Case    ${TESTNAME}: Called with embedded args
    Check Test Case    ${TESTNAME}: Called with exact name
    Length Should Be    ${ERRORS}    4

Using keyword defined multiple times in resource fails
    Check Test Case    ${TESTNAME}
    Creating keyword should have failed    3    Defined Twice In Resource   5
    ...    dupe_keywords.resource

Keyword with embedded arguments defined multiple times in resource fails at run-time
    Check Test Case    ${TESTNAME}
    Length Should Be    ${ERRORS}    4

*** Keywords ***
Creating keyword should have failed
    [Arguments]    ${index}    ${name}    ${lineno}    ${source}=duplicate_user_keywords.robot
    Error In File    ${index}    keywords/${source}    ${lineno}
    ...    Creating keyword '${name}' failed:
    ...    Keyword with same name defined multiple times.

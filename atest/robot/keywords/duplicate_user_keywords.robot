*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    keywords/duplicate_user_keywords.robot
Resource         atest_resource.robot

*** Test Cases ***
Using keyword defined twice fails
    Check Test Case    ${TESTNAME}
    Creating keyword should have failed    0    Defined Twice

Using keyword defined thrice fails as well
    Check Test Case    ${TESTNAME}
    Creating keyword should have failed    1    Defined Thrice
    Creating keyword should have failed    2    DEFINED THRICE

Keyword with embedded arguments defined twice fails at run-time
    Check Test Case    ${TESTNAME}: Called with embedded args
    Check Test Case    ${TESTNAME}: Called with exact name
    Length Should Be    ${ERRORS}    4

Using keyword defined multiple times in resource fails
    Check Test Case    ${TESTNAME}
    Creating keyword should have failed    3    Defined Twice In Resource
    ...    dupe_keywords.robot    resource

Keyword with embedded arguments defined multiple times in resource fails at run-time
    Check Test Case    ${TESTNAME}
    Length Should Be    ${ERRORS}    4

*** Keywords ***
Creating keyword should have failed
    [Arguments]    ${index}    ${name}    ${source}=duplicate_user_keywords.robot    ${source type}=test case
    ${source} =    Normalize Path    ${DATADIR}/keywords/${source}
    ${message} =    Catenate
    ...    Error in ${source type} file '${source}':
    ...    Creating keyword '${name}' failed:
    ...    Keyword with same name defined multiple times.
    Check Log Message    ${ERRORS[${index}]}    ${message}    ERROR

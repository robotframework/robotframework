*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    keywords/duplicate_static_keywords.robot
Resource         atest_resource.robot

*** Test Cases ***
Using keyword defined twice fails
    ${tc} =    Check Test Case    ${TESTNAME}
    Should Be Equal    ${tc.kws[0].full_name}    DupeKeywords.Defined Twice
    Creating keyword should have failed    2    Defined twice

Using keyword defined thrice fails as well
    ${tc} =    Check Test Case    ${TESTNAME}
    Should Be Equal    ${tc.kws[0].full_name}    DupeKeywords.Defined Thrice
    Creating keyword should have failed    0    Defined Thrice
    Creating keyword should have failed    1    Defined Thrice

Keyword with embedded arguments defined twice fails at run-time
    ${tc} =    Check Test Case    ${TESTNAME}: Called with embedded args
    Should Be Equal    ${tc.kws[0].full_name}    Embedded arguments twice
    ${tc} =    Check Test Case    ${TESTNAME}: Called with exact name
    Should Be Equal    ${tc.kws[0].full_name}    Embedded \${arguments match} twice
    Length Should Be    ${ERRORS}    3

*** Keywords ***
Creating keyword should have failed
    [Arguments]    ${index}    ${name}
    Error in library    DupeKeywords
    ...    Adding keyword '${name}' failed:
    ...    Keyword with same name defined multiple times.
    ...    index=${index}

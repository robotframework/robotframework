*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    keywords/duplicate_dynamic_keywords.robot
Resource         atest_resource.robot

*** Test Cases ***
Using keyword defined multiple times fails
    ${tc} =    Check Test Case    ${TESTNAME}
    Should Be Equal    ${tc.kws[0].name}    DupeDynamicKeywords.DEFINED TWICE
    Creating keyword should have failed    0    DEFINED TWICE

Keyword with embedded arguments defined multiple times fails at run-time
    ${tc} =    Check Test Case    ${TESTNAME}
    Should Be Equal    ${tc.kws[0].name}    Embedded twice
    Length Should Be    ${ERRORS}    1

Exact duplicate is accepted
    Check Test Case    ${TESTNAME}

*** Keywords ***
Creating keyword should have failed
    [Arguments]    ${index}    ${name}
    ${message} =    Catenate
    ...    Adding keyword '${name}' to library 'DupeDynamicKeywords' failed:
    ...    Keyword with same name defined multiple times.
    Check Log Message    ${ERRORS}[${index}]    ${message}    ERROR

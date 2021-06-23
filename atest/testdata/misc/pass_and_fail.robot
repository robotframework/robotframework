*** Setting ***
Documentation     Some tests here
Suite Setup       My Keyword    Suite Setup
Force Tags        force
Library           String

*** Variable ***
${LEVEL1}         INFO
${LEVEL2}         DEBUG

*** Test Case ***
Pass
    [Tags]    pass
    # I am a comment. Please ignore me.
    My Keyword    Pass

Fail
    [Documentation]    FAIL Expected failure
    [Tags]    fail
    My Keyword    Fail
    Fail    Expected failure

*** Keyword ***
My Keyword
    [Arguments]    ${who}
    [Tags]    keyword    tags    force
    Log    Hello says "${who}"!    ${LEVEL1}
    Log    Debug message    ${LEVEL2}
    ${assign} =    Convert to Uppercase    Just testing...

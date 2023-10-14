*** Settings ***
Documentation     Some tests here
Suite Setup       My Keyword    Suite Setup
Test Tags         force
Library           String

*** Variables ***
${LEVEL1}         INFO
${LEVEL2}         DEBUG

*** Test Cases ***
Pass
    [Tags]    pass
    # I am a comment. Please ignore me.
    My Keyword    Pass

Fail
    [Documentation]    FAIL Expected failure
    [Tags]    fail
    My Keyword    Fail
    Fail    Expected failure

*** Keywords ***
My Keyword
    [Arguments]    ${who}
    [Tags]    keyword    tags    force
    Log    Hello says "${who}"!    ${LEVEL1}
    Log    Debug message    ${LEVEL2}
    ${assign} =    Convert to Uppercase    Just testing...
    VAR    ${expected}    JUST TESTING...
    Should Be Equal    ${assign}    ${expected}
    RETURN

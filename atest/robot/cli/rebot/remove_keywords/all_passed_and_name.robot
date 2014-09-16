*** Settings ***
Documentation     Testing ALL and PASSED modes with --RemoveKeywords option.
Suite Setup       Run Some Tests
Suite Teardown    Remove File    ${INPUTFILE}
Force Tags        regression    pybot    jybot
Resource          remove_keywords_resource.robot

*** Test Cases ***
All Mode
    [Setup]    Run Rebot and Set My Suite    --RemoveKeywords ALL    0
    Keyword Should Be Empty    ${MY SUITE.setup}    My Keyword    Suite Setup
    Keyword Should Contain Removal Message    ${MY SUITE.setup}
    ${tc1}    ${tc2} =    Set Variable    ${MY SUITE.tests}
    Length Should Be    ${tc1.kws}    1
    Keyword Should Be Empty    ${tc1.kws[0]}    My Keyword    Pass
    Length Should Be    ${tc2.kws}    2
    Keyword Should Be Empty    ${tc2.kws[0]}    My Keyword    Fail
    Keyword Should Be Empty    ${tc2.kws[1]}    BuiltIn.Fail    Expected failure
    Keyword Should Contain Removal Message    ${tc2.kws[1]}   Fails the test with the given message and optionally alters its tags.

Warnings Are Removed In All Mode
    [Setup]    Run Rebot and Set My Suite    --removekeywords All    1
    Keyword Should Be Empty    ${MY SUITE.setup}    Warning in    suite setup
    Keyword Should Be Empty    ${MY SUITE.teardown}    Warning in    suite teardown
    ${tc1}    ${tc2}=    Set Variable    ${MY SUITE.tests}
    Length Should Be    ${tc1.kws}    1
    Length Should Be    ${tc2.kws}    1
    Keyword Should Be Empty    ${tc1.kws[0]}    Warning in    test case
    Keyword Should Be Empty    ${tc2.kws[0]}    BuiltIn.Log    No warnings here

Passed Mode
    [Setup]    Run Rebot and Set My Suite    --removekeywords passed    0
    Keyword Should Not Be Empty    ${MY SUITE.setup}    My Keyword    Suite Setup
    ${tc1}    ${tc2} =    Set Variable    ${MY SUITE.tests}
    Length Should Be    ${tc1.kws}    1
    Keyword Should Be Empty    ${tc1.keywords[0]}    My Keyword    Pass
    Keyword Should Contain Removal Message     ${tc1.keywords[0]}
    Length Should Be    ${tc2.kws}    2
    Keyword Should Not Be Empty    ${tc2.kws[0]}    My Keyword    Fail
    Keyword Should Not Be Empty    ${tc2.kws[1]}    BuiltIn.Fail    Expected failure

Warnings Are Not Removed In Passed Mode
    [Setup]    Run Rebot and Set My Suite    --removekeywords Passed    1
    Keyword Should Not Be Empty    ${MY SUITE.setup}    Warning in    suite setup
    Keyword Should Not Be Empty    ${MY SUITE.teardown}    Warning in    suite teardown
    ${tc1}    ${tc2}=    Set Variable    ${MY SUITE.tests}
    Length Should Be    ${tc1.kws}    1
    Keyword Should Not Be Empty    ${tc1.kws[0]}    Warning in    test case
    Keyword Should Not Be Empty    ${tc1.kws[0].kws[0]}    BuiltIn.Log    Warning in \${where}    WARN
    Length Should Be    ${tc2.kws}    1
    Keyword Should Be Empty    ${tc2.kws[0]}    BuiltIn.Log    No warnings here

Name Mode
    [Setup]    Run Rebot and Set My Suite    --removekeywords name:BuiltIn.Fail --RemoveK NAME:??_KEYWORD    0
    Keyword Should Be Empty    ${MY SUITE.setup}    My Keyword    Suite Setup
    Keyword Should Contain Removal Message    ${MY SUITE.setup}
    ${tc1}    ${tc2} =    Set Variable    ${MY SUITE.tests}
    Length Should Be    ${tc1.kws}    1
    Keyword Should Be Empty    ${tc1.kws[0]}    My Keyword    Pass
    Keyword Should Contain Removal Message    ${tc1.kws[0]}
    Length Should Be    ${tc2.kws}    2
    Keyword Should Be Empty    ${tc2.kws[0]}    My Keyword    Fail
    Keyword Should Contain Removal Message    ${tc2.kws[0]}
    Keyword Should Be Empty    ${tc2.kws[1]}    BuiltIn.Fail    Expected failure
    Keyword Should Contain Removal Message    ${tc2.kws[0]}

Warnings Are Not Removed In Name Mode
    [Setup]    Run Rebot and Set My Suite    --removekeywords NaMe:BuiltIn.Log --RemoveK NaMe:W*IN    1
    Keyword Should Not Be Empty    ${MY SUITE.setup}    Warning in    suite setup
    Keyword Should Not Be Empty    ${MY SUITE.teardown}    Warning in    suite teardown
    ${tc1}    ${tc2}=    Set Variable    ${MY SUITE.tests}
    Length Should Be    ${tc1.kws}    1
    Length Should Be    ${tc2.kws}    1
    Keyword Should Not Be Empty    ${tc1.kws[0]}    Warning in    test case
    Keyword Should Not Be Empty    ${tc1.kws[0].kws[0]}    BuiltIn.Log    Warning in \${where}    WARN
    Keyword Should Be Empty    ${tc2.kws[0]}    BuiltIn.Log    No warnings here

*** Keywords ***
Run Some Tests
    Create Output With Robot    ${INPUTFILE}    ${EMPTY}    misc/pass_and_fail.robot    misc/warnings_and_errors.robot

Run Rebot And Set My Suite
    [Arguments]    ${rebot params}    ${suite index}
    Run Rebot    ${rebot params}    ${INPUTFILE}
    Should Not Be Equal    ${SUITE}    ${None}    Errors in test execution
    Set Test Variable    ${MY SUITE}    ${SUITE.suites[${suite index}]}

Keyword Should Contain Removal Message
    [Arguments]    ${keyword}    ${doc}=${EMPTY}
    ${expected} =    Set Variable    ${doc}\n\n_Keyword data removed using --RemoveKeywords option._
    Should Be Equal  ${keyword.doc}  ${expected.strip()}

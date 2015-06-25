*** Settings ***
Suite Setup       Run Some Tests
Suite Teardown    Remove File    ${INPUTFILE}
Force Tags        regression    pybot    jybot
Resource          remove_keywords_resource.robot

*** Test Cases ***
All Mode
    [Setup]    Run Rebot and set My Suite    --RemoveKeywords ALL    0
    Keyword Should Be Empty    ${MY SUITE.setup}    My Keyword    Suite Setup
    Keyword Should Contain Removal Message    ${MY SUITE.setup}
    ${tc1} =    Check Test Case    Pass
    ${tc2} =    Check Test Case    Fail
    Length Should Be    ${tc1.kws}    1
    Keyword Should Be Empty    ${tc1.kws[0]}    My Keyword    Pass
    Length Should Be    ${tc2.kws}    2
    Keyword Should Be Empty    ${tc2.kws[0]}    My Keyword    Fail
    Keyword Should Be Empty    ${tc2.kws[1]}    BuiltIn.Fail    Expected failure
    Keyword Should Contain Removal Message    ${tc2.kws[1]}   Fails the test with the given message and optionally alters its tags.

Warnings Are Removed In All Mode
    [Setup]    Verify previous test and set My Suite    All Mode    1
    Keyword Should Be Empty    ${MY SUITE.setup}    Warning in    suite setup
    Keyword Should Be Empty    ${MY SUITE.teardown}    Warning in    suite teardown
    ${tc1}    ${tc2}=    Set Variable    ${MY SUITE.tests[:2]}
    Length Should Be    ${tc1.kws}    1
    Length Should Be    ${tc2.kws}    1
    Keyword Should Be Empty    ${tc1.kws[0]}    Warning in    test case
    Keyword Should Be Empty    ${tc2.kws[0]}    No warning
    Logged Warnings Are Preserved In Execution Errors

Errors Are Removed In All Mode
    [Setup]    Previous test should have passed    Warnings Are Removed In All Mode
    ${tc} =    Check Test Case    Error in test case
    Keyword Should Be Empty    ${tc.kws[0]}    Error in test case
    Logged Errors Are Preserved In Execution Errors

Passed Mode
    [Setup]    Run Rebot and set My Suite    --removekeywords passed    0
    Keyword Should Not Be Empty    ${MY SUITE.setup}    My Keyword    Suite Setup
    ${tc1} =    Check Test Case    Pass
    ${tc2} =    Check Test Case    Fail
    Length Should Be    ${tc1.kws}    1
    Keyword Should Be Empty    ${tc1.keywords[0]}    My Keyword    Pass
    Keyword Should Contain Removal Message     ${tc1.keywords[0]}
    Length Should Be    ${tc2.kws}    2
    Keyword Should Not Be Empty    ${tc2.kws[0]}    My Keyword    Fail
    Keyword Should Not Be Empty    ${tc2.kws[1]}    BuiltIn.Fail    Expected failure

Warnings Are Not Removed In Passed Mode
    [Setup]    Verify previous test and set My Suite    Passed Mode    1
    Keyword Should Not Be Empty    ${MY SUITE.setup}    Warning in    suite setup
    Keyword Should Not Be Empty    ${MY SUITE.teardown}    Warning in    suite teardown
    ${tc1}    ${tc2}=    Set Variable    ${MY SUITE.tests[:2]}
    Length Should Be    ${tc1.kws}    1
    Keyword Should Not Be Empty    ${tc1.kws[0]}    Warning in    test case
    Keyword Should Not Be Empty    ${tc1.kws[0].kws[0]}    BuiltIn.Log    Warning in \${where}    WARN
    Length Should Be    ${tc2.kws}    1
    Keyword Should Be Empty    ${tc2.kws[0]}    No warning
    Logged Warnings Are Preserved In Execution Errors

Errors Are Not Removed In Passed Mode
    [Setup]    Previous test should have passed    Warnings Are Not Removed In Passed Mode
    ${tc} =    Check Test Case    Error in test case
    Check Log Message    ${tc.kws[0].kws[0].msgs[0]}    Logged errors supported since 2.9    ERROR
    Logged Errors Are Preserved In Execution Errors

Name Mode
    [Setup]    Run Rebot and set My Suite
    ...    --removekeywords name:BuiltIn.Fail --RemoveK NAME:??_KEYWORD --RemoveK NaMe:*WARN*IN* --removek name:errorin*   0
    Keyword Should Be Empty    ${MY SUITE.setup}    My Keyword    Suite Setup
    Keyword Should Contain Removal Message    ${MY SUITE.setup}
    ${tc1} =    Check Test Case    Pass
    ${tc2} =    Check Test Case    Fail
    Length Should Be    ${tc1.kws}    1
    Keyword Should Be Empty    ${tc1.kws[0]}    My Keyword    Pass
    Keyword Should Contain Removal Message    ${tc1.kws[0]}
    Length Should Be    ${tc2.kws}    2
    Keyword Should Be Empty    ${tc2.kws[0]}    My Keyword    Fail
    Keyword Should Contain Removal Message    ${tc2.kws[0]}
    Keyword Should Be Empty    ${tc2.kws[1]}    BuiltIn.Fail    Expected failure
    Keyword Should Contain Removal Message    ${tc2.kws[0]}

Warnings Are Not Removed In Name Mode
    [Setup]    Verify previous test and set My Suite    Name Mode    1
    Keyword Should Not Be Empty    ${MY SUITE.setup}    Warning in    suite setup
    Keyword Should Not Be Empty    ${MY SUITE.teardown}    Warning in    suite teardown
    ${tc1}    ${tc2}=    Set Variable    ${MY SUITE.tests[:2]}
    Length Should Be    ${tc1.kws}    1
    Length Should Be    ${tc2.kws}    1
    Keyword Should Not Be Empty    ${tc1.kws[0]}    Warning in    test case
    Keyword Should Not Be Empty    ${tc1.kws[0].kws[0]}    BuiltIn.Log    Warning in \${where}    WARN
    Keyword Should Be Empty    ${tc2.kws[0]}    No warning
    Logged Warnings Are Preserved In Execution Errors

Errors Are Not Removed In Name Mode
    [Setup]    Previous test should have passed    Warnings Are Not Removed In Name Mode
    ${tc} =    Check Test Case    Error in test case
    Check Log Message    ${tc.kws[0].kws[0].msgs[0]}    Logged errors supported since 2.9    ERROR
    Logged Errors Are Preserved In Execution Errors

Tag Mode
    [Setup]    Run Rebot and set My Suite    --removekeywords tag:force --RemoveK TAG:warn    0
    Keyword Should Be Empty    ${MY SUITE.setup}    My Keyword    Suite Setup
    Keyword Should Contain Removal Message    ${MY SUITE.setup}
    ${tc1} =    Check Test Case    Pass
    ${tc2} =    Check Test Case    Fail
    Length Should Be    ${tc1.kws}    1
    Keyword Should Be Empty    ${tc1.kws[0]}    My Keyword    Pass
    Keyword Should Contain Removal Message    ${tc1.kws[0]}
    Length Should Be    ${tc2.kws}    2
    Keyword Should Be Empty    ${tc2.kws[0]}    My Keyword    Fail
    Keyword Should Contain Removal Message    ${tc2.kws[0]}
    Keyword Should Not Be Empty    ${tc2.kws[1]}    BuiltIn.Fail    Expected failure

Warnings Are Not Removed In Tag Mode
    [Setup]    Verify previous test and set My Suite    Tag Mode    1
    Keyword Should Not Be Empty    ${MY SUITE.setup}    Warning in    suite setup
    Keyword Should Not Be Empty    ${MY SUITE.teardown}    Warning in    suite teardown
    ${tc1}    ${tc2}=    Set Variable    ${MY SUITE.tests[:2]}
    Length Should Be    ${tc1.kws}    1
    Length Should Be    ${tc2.kws}    1
    Keyword Should Not Be Empty    ${tc1.kws[0]}    Warning in    test case
    Keyword Should Not Be Empty    ${tc1.kws[0].kws[0]}    BuiltIn.Log    Warning in \${where}    WARN
    Keyword Should Be Empty    ${tc2.kws[0]}    No warning
    Logged Warnings Are Preserved In Execution Errors

Errors Are Not Removed In Tag Mode
    [Setup]    Previous test should have passed    Warnings Are Not Removed In Tag Mode
    ${tc} =    Check Test Case    Error in test case
    Check Log Message    ${tc.kws[0].kws[0].msgs[0]}    Logged errors supported since 2.9    ERROR
    Logged Errors Are Preserved In Execution Errors

*** Keywords ***
Run Some Tests
    Create Output With Robot    ${INPUTFILE}    ${EMPTY}    misc/pass_and_fail.robot    misc/warnings_and_errors.robot

Run Rebot And Set My Suite
    [Arguments]    ${rebot params}    ${suite index}
    Run Rebot    ${rebot params}    ${INPUTFILE}
    Should Not Be Equal    ${SUITE}    ${None}    Errors in test execution
    Set Test Variable    ${MY SUITE}    ${SUITE.suites[${suite index}]}

Verify previous test and set My Suite
    [Arguments]    ${prev test}    ${suite index}
    Previous test should have passed    ${prev test}
    Set Test Variable    ${MY SUITE}    ${SUITE.suites[${suite index}]}

Keyword Should Contain Removal Message
    [Arguments]    ${keyword}    ${doc}=${EMPTY}
    ${expected} =    Set Variable    ${doc}\n\n_Keyword data removed using --RemoveKeywords option._
    Should Be Equal  ${keyword.doc}  ${expected.strip()}

Logged Warnings Are Preserved In Execution Errors
    Check Log Message    ${ERRORS[1]}    Warning in suite setup    WARN
    Check Log Message    ${ERRORS[2]}    Warning in test case    WARN
    Check Log Message    ${ERRORS[5]}    Warning in suite teardown    WARN

Logged Errors Are Preserved In Execution Errors
    Check Log Message    ${ERRORS[4]}    Logged errors supported since 2.9    ERROR

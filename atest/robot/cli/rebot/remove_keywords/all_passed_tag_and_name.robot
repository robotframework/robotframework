*** Settings ***
Suite Setup       Run Some Tests
Suite Teardown    Remove File    ${INPUTFILE}
Resource          remove_keywords_resource.robot

*** Test Cases ***
All Mode
    [Setup]    Run Rebot and set My Suite    --RemoveKeywords ALL    0
    Keyword Should Be Empty    ${MY SUITE.setup}    My Keyword    Suite Setup
    Keyword Should Contain Removal Message    ${MY SUITE.setup}
    ${tc1} =    Check Test Case    Pass
    ${tc2} =    Check Test Case    Fail
    Length Should Be    ${tc1.body}    1
    Keyword Should Be Empty    ${tc1.body[0]}    My Keyword    Pass
    Length Should Be    ${tc2.body}    2
    Keyword Should Be Empty    ${tc2.body[0]}    My Keyword    Fail
    Keyword Should Be Empty    ${tc2.body[1]}    BuiltIn.Fail    Expected failure
    Keyword Should Contain Removal Message    ${tc2.body[1]}   Expected failure
    ${tc3} =    Check Test Case    Test with setup and teardown
    Keyword Should Be Empty    ${tc3.setup}       Test Setup
    Keyword Should Contain Removal Message    ${tc3.setup}
    Keyword Should Be Empty    ${tc3.teardown}    Test Teardown
    Keyword Should Contain Removal Message    ${tc3.teardown}

Warnings Are Removed In All Mode
    [Setup]    Verify previous test and set My Suite    All Mode    1
    Keyword Should Be Empty    ${MY SUITE.setup}    Warning in    suite setup
    Keyword Should Be Empty    ${MY SUITE.teardown}    Warning in    suite teardown
    ${tc1}    ${tc2}=    Set Variable    ${MY SUITE.tests[:2]}
    Length Should Be    ${tc1.body}    1
    Length Should Be    ${tc2.body}    1
    Keyword Should Be Empty    ${tc1.body[0]}    Warning in    test case
    Keyword Should Be Empty    ${tc2.body[0]}    No warning
    Logged Warnings Are Preserved In Execution Errors

Errors Are Removed In All Mode
    ${tc} =    Check Test Case    Error in test case
    Keyword Should Be Empty    ${tc.body[0]}    Error in test case
    Logged Errors Are Preserved In Execution Errors

IF/ELSE in All mode
    ${tc} =    Check Test Case    IF structure
    Length Should Be    ${tc.body}            2
    Length Should Be    ${tc.body[1].body}    3
    IF Branch Should Be Empty    ${tc.body[1].body[0]}    IF         '\${x}' == 'wrong'
    IF Branch Should Be Empty    ${tc.body[1].body[1]}    ELSE IF    '\${x}' == 'value'
    IF Branch Should Be Empty    ${tc.body[1].body[2]}    ELSE

FOR in All mode
    ${tc} =    Check Test Case    FOR
    Length Should Be    ${tc.body}    1
    FOR Loop Should Be Empty    ${tc.body[0]}    IN
    ${tc} =    Check Test Case    FOR IN RANGE
    Length Should Be    ${tc.body}    1
    FOR Loop Should Be Empty    ${tc.body[0]}    IN RANGE

TRY/EXCEPT in All mode
    ${tc} =    Check Test Case    Everything
    Length Should Be    ${tc.body}            1
    Length Should Be    ${tc.body[0].body}    5
    TRY Branch Should Be Empty    ${tc.body[0].body[0]}    TRY        Ooops!<hr>
    TRY Branch Should Be Empty    ${tc.body[0].body[1]}    EXCEPT
    TRY Branch Should Be Empty    ${tc.body[0].body[2]}    EXCEPT
    TRY Branch Should Be Empty    ${tc.body[0].body[3]}    ELSE
    TRY Branch Should Be Empty    ${tc.body[0].body[4]}    FINALLY

WHILE and VAR in All mode
    ${tc} =    Check Test Case    WHILE loop executed multiple times
    Length Should Be    ${tc.body}               2
    Should Be Equal     ${tc.body[1].type}       WHILE
    Should Be Empty     ${tc.body[1].body}
    Should Be Equal     ${tc.body[1].message}    *HTML* ${DATA REMOVED}

VAR in All mode
    ${tc} =    Check Test Case    IF structure
    Should Be Equal     ${tc.body[0].type}       VAR
    Should Be Empty     ${tc.body[0].body}
    Should Be Equal     ${tc.body[0].message}    *HTML* ${DATA REMOVED}
    ${tc} =    Check Test Case    WHILE loop executed multiple times
    Should Be Equal     ${tc.body[0].type}       VAR
    Should Be Empty     ${tc.body[0].body}
    Should Be Equal     ${tc.body[0].message}    *HTML* ${DATA REMOVED}

Passed Mode
    [Setup]    Run Rebot and set My Suite    --removekeywords passed    0
    Keyword Should Not Be Empty    ${MY SUITE.setup}    My Keyword    Suite Setup
    ${tc1} =    Check Test Case    Pass
    ${tc2} =    Check Test Case    Fail
    Length Should Be    ${tc1.body}    1
    Keyword Should Be Empty    ${tc1.body[0]}    My Keyword    Pass
    Keyword Should Contain Removal Message     ${tc1.body[0]}
    Length Should Be    ${tc2.body}    2
    Keyword Should Not Be Empty    ${tc2.body[0]}    My Keyword    Fail
    Keyword Should Not Be Empty    ${tc2.body[1]}    BuiltIn.Fail    Expected failure
    ${tc3} =    Check Test Case    Test with setup and teardown
    Keyword Should Be Empty    ${tc3.setup}       Test Setup
    Keyword Should Contain Removal Message    ${tc3.setup}
    Keyword Should Be Empty    ${tc3.teardown}    Test Teardown
    Keyword Should Contain Removal Message    ${tc3.teardown}

Warnings Are Not Removed In Passed Mode
    [Setup]    Verify previous test and set My Suite    Passed Mode    1
    Keyword Should Not Be Empty    ${MY SUITE.setup}    Warning in    suite setup
    Keyword Should Not Be Empty    ${MY SUITE.teardown}    Warning in    suite teardown
    ${tc1}    ${tc2}=    Set Variable    ${MY SUITE.tests[:2]}
    Length Should Be    ${tc1.body}    1
    Keyword Should Not Be Empty    ${tc1.body[0]}    Warning in    test case
    Keyword Should Not Be Empty    ${tc1.body[0].body[0].body[0].body[0]}    BuiltIn.Log    Warning in \${where}    WARN
    Length Should Be    ${tc2.body}    1
    Keyword Should Be Empty    ${tc2.body[0]}    No warning
    Logged Warnings Are Preserved In Execution Errors

Errors Are Not Removed In Passed Mode
    [Setup]    Previous test should have passed    Warnings Are Not Removed In Passed Mode
    ${tc} =    Check Test Case    Error in test case
    Check Log Message    ${tc.body[0].body[0].msgs[0]}    Logged errors supported since 2.9    ERROR
    Logged Errors Are Preserved In Execution Errors

Name Mode
    [Setup]    Run Rebot and set My Suite
    ...    --removekeywords name:BuiltIn.Fail --RemoveK NAME:??_KEYWORD --RemoveK NaMe:*WARN*IN* --removek name:errorin*   0
    Keyword Should Be Empty    ${MY SUITE.setup}    My Keyword    Suite Setup
    Keyword Should Contain Removal Message    ${MY SUITE.setup}
    ${tc1} =    Check Test Case    Pass
    ${tc2} =    Check Test Case    Fail
    Length Should Be    ${tc1.body}    1
    Keyword Should Be Empty    ${tc1.body[0]}    My Keyword    Pass
    Keyword Should Contain Removal Message    ${tc1.body[0]}
    Length Should Be    ${tc2.body}    2
    Keyword Should Be Empty    ${tc2.body[0]}    My Keyword    Fail
    Keyword Should Contain Removal Message    ${tc2.body[0]}
    Keyword Should Be Empty    ${tc2.body[1]}    BuiltIn.Fail    Expected failure
    Keyword Should Contain Removal Message    ${tc2.body[0]}

Warnings Are Not Removed In Name Mode
    [Setup]    Verify previous test and set My Suite    Name Mode    1
    Keyword Should Not Be Empty    ${MY SUITE.setup}    Warning in    suite setup
    Keyword Should Not Be Empty    ${MY SUITE.teardown}    Warning in    suite teardown
    ${tc1}    ${tc2}=    Set Variable    ${MY SUITE.tests[:2]}
    Length Should Be    ${tc1.body}    1
    Length Should Be    ${tc2.body}    1
    Keyword Should Not Be Empty    ${tc1.body[0]}    Warning in    test case
    Keyword Should Not Be Empty    ${tc1.body[0].body[0].body[0].body[0]}    BuiltIn.Log    Warning in \${where}    WARN
    Keyword Should Be Empty    ${tc2.body[0]}    No warning
    Logged Warnings Are Preserved In Execution Errors

Errors Are Not Removed In Name Mode
    [Setup]    Previous test should have passed    Warnings Are Not Removed In Name Mode
    ${tc} =    Check Test Case    Error in test case
    Check Log Message    ${tc.body[0].body[0].msgs[0]}    Logged errors supported since 2.9    ERROR
    Logged Errors Are Preserved In Execution Errors

Tag Mode
    [Setup]    Run Rebot and set My Suite    --removekeywords tag:force --RemoveK TAG:warn    0
    Keyword Should Be Empty    ${MY SUITE.setup}    My Keyword    Suite Setup
    Keyword Should Contain Removal Message    ${MY SUITE.setup}
    ${tc1} =    Check Test Case    Pass
    ${tc2} =    Check Test Case    Fail
    Length Should Be    ${tc1.body}    1
    Keyword Should Be Empty    ${tc1.body[0]}    My Keyword    Pass
    Keyword Should Contain Removal Message    ${tc1.body[0]}
    Length Should Be    ${tc2.body}    2
    Keyword Should Be Empty    ${tc2.body[0]}    My Keyword    Fail
    Keyword Should Contain Removal Message    ${tc2.body[0]}
    Keyword Should Not Be Empty    ${tc2.body[1]}    BuiltIn.Fail    Expected failure

Warnings Are Not Removed In Tag Mode
    [Setup]    Verify previous test and set My Suite    Tag Mode    1
    Keyword Should Not Be Empty    ${MY SUITE.setup}    Warning in    suite setup
    Keyword Should Not Be Empty    ${MY SUITE.teardown}    Warning in    suite teardown
    ${tc1}    ${tc2}=    Set Variable    ${MY SUITE.tests[:2]}
    Length Should Be    ${tc1.body}    1
    Length Should Be    ${tc2.body}    1
    Keyword Should Not Be Empty    ${tc1.body[0]}    Warning in    test case
    Keyword Should Not Be Empty    ${tc1.body[0].body[0].body[0].body[0]}    BuiltIn.Log    Warning in \${where}    WARN
    Keyword Should Be Empty    ${tc2.body[0]}    No warning
    Logged Warnings Are Preserved In Execution Errors

Errors Are Not Removed In Tag Mode
    [Setup]    Previous test should have passed    Warnings Are Not Removed In Tag Mode
    ${tc} =    Check Test Case    Error in test case
    Check Log Message    ${tc.body[0].body[0].msgs[0]}    Logged errors supported since 2.9    ERROR
    Logged Errors Are Preserved In Execution Errors

*** Keywords ***
Run Some Tests
    ${suites} =    Catenate
    ...    misc/pass_and_fail.robot
    ...    misc/warnings_and_errors.robot
    ...    misc/if_else.robot
    ...    misc/for_loops.robot
    ...    misc/try_except.robot
    ...    misc/while.robot
    ...    misc/setups_and_teardowns.robot
    Create Output With Robot    ${INPUTFILE}    ${EMPTY}    ${suites}

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
    [Arguments]    ${keyword}    ${message}=
    IF    $message
        ${message} =    Set Variable    ${message}<hr>
    END
    Should Be Equal    ${keyword.message}    *HTML* ${message}${DATA REMOVED}

Logged Warnings Are Preserved In Execution Errors
    Check Log Message    ${ERRORS[1]}    Warning in suite setup    WARN
    Check Log Message    ${ERRORS[2]}    Warning in test case    WARN
    Check Log Message    ${ERRORS[5]}    Warning in suite teardown    WARN

Logged Errors Are Preserved In Execution Errors
    Check Log Message    ${ERRORS[4]}    Logged errors supported since 2.9    ERROR

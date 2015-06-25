*** Settings ***
Force Tags        regression    jybot    pybot
Resource          atest_resource.robot

*** Variables ***
${1 PASS MSG}     1 critical test, 1 passed, 0 failed\n 1 test total, 1 passed, 0 failed
${1 FAIL MSG}     1 critical test, 0 passed, 1 failed\n 1 test total, 0 passed, 1 failed
${2 FAIL MSG}     2 critical tests, 0 passed, 2 failed\n 2 tests total, 0 passed, 2 failed
${4 FAIL MSG}     4 critical tests, 0 passed, 4 failed\n 4 tests total, 0 passed, 4 failed
${5 FAIL MSG}     5 critical tests, 0 passed, 5 failed\n 5 tests total, 0 passed, 5 failed
${12 FAIL MSG}    12 critical tests, 0 passed, 12 failed\n 12 tests total, 0 passed, 12 failed
${ALSO}           \n\nAlso teardown of the parent suite failed.
${EXECUTED FILE}    %{TEMPDIR}/robot-suite-teardown-executed.txt

*** Test Cases ***
Passing Suite Setup
    Run Tests    ${EMPTY}    core/passing_suite_setup.robot
    Check Suite Status    ${SUITE}    PASS    ${1 PASS MSG}
    ...    Verify Suite Setup

Passing Suite Teardown
    [Setup]    Remove File    ${EXECUTED FILE}
    Run Tests    ${EMPTY}    core/passing_suite_teardown.robot
    Check Suite Status    ${SUITE}    PASS    ${1 PASS MSG}
    ...   Test
    File Should Exist    ${EXECUTED FILE}
    [Teardown]    Remove File    ${EXECUTED FILE}

Passing Suite Setup And Teardown
    [Setup]    Remove File    ${EXECUTED FILE}
    Run Tests    ${EMPTY}    core/passing_suite_setup_and_teardown.robot
    Check Suite Status    ${SUITE}    PASS    ${1 PASS MSG}
    ...    Verify Suite Setup
    File Should Exist    ${EXECUTED FILE}
    [Teardown]    Remove File    ${EXECUTED FILE}

Failing Suite Setup
    Run Tests    ${EMPTY}    core/failing_suite_setup.robot
    Check Suite Status    ${SUITE}    FAIL
    ...    Suite setup failed:\nExpected failure\n\n${2 FAIL MSG}
    ...    Test 1    Test 2
    Should Be Equal    ${SUITE.setup.status}    FAIL
    Should Be Equal    ${SUITE.teardown.status}    PASS
    Length Should Be    ${SUITE.teardown.msgs}    1
    Check Log Message    ${SUITE.teardown.messages[0]}    Suite teardown executed
    Should Be Empty    ${SUITE.teardown.kws}

Erroring Suite Setup
    Run Tests    ${EMPTY}    core/erroring_suite_setup.robot
    Check Suite Status    ${SUITE}    FAIL
    ...    Suite setup failed:\nNo keyword with name 'Non-Existing Keyword' found.\n\n${2 FAIL MSG}
    ...    Test 1    Test 2
    Should Be Equal    ${SUITE.setup.status}    FAIL
    ${td} =    Set Variable    ${SUITE.teardown}
    Should Be Equal    ${td.name}    My TD
    Should Be Equal    ${td.status}    PASS
    Should Be Empty    ${td.msgs}
    Length Should Be    ${td.kws}    2
    Length Should Be    ${td.kws[0].msgs}    1
    Check Log Message    ${td.kws[0].msgs[0]}    Hello from suite teardown!
    Should Be Empty    ${td.kws[0].kws}
    Should Be Equal    ${td.kws[1].name}    BuiltIn.No Operation

Failing Higher Level Suite Setup
    Run Tests    ${EMPTY}    core/failing_higher_level_suite_setup
    Check Suite Status    ${SUITE}    FAIL
    ...    Suite setup failed:\nExpected failure in higher level setup\n\n${2 FAIL MSG}
    ...    Test 1    Test 2
    Check Suite Status    ${SUITE.suites[0]}    FAIL
    ...    Parent suite setup failed:\nExpected failure in higher level setup\n\n${1 FAIL MSG}
    ...    Test 1
    Check Suite Status    ${SUITE.suites[1]}    FAIL
    ...    Parent suite setup failed:\nExpected failure in higher level setup\n\n${1 FAIL MSG}
    ...    Test 2
    Stderr Should Be Empty

Failing Suite Teardown When All Tests Pass
    Run Tests    ${EMPTY}    core/failing_suite_teardown.robot
    ${error} =    Catenate    SEPARATOR=\n\n
    ...    Several failures occurred:
    ...    1) first
    ...    2) second
    Check Suite Status    ${SUITE}    FAIL
    ...    Suite teardown failed:\n${error}\n\n${2 FAIL MSG}
    ...    Test 1    Test 2
    Should Be Equal    ${SUITE.teardown.status}    FAIL
    Output should contain teardown error    ${error}

Failing Suite Teardown When Also Tests Fail
    Run Tests    ${EMPTY}    core/failing_suite_teardown_2.robot
    Check Suite Status    ${SUITE}    FAIL
    ...    Suite teardown failed:\nExpected failure\n\n${5 FAIL MSG}
    ...    Test Passes    Test Fails    Setup Fails    Teardown Fails    Test and Teardown Fail
    Should Be Equal    ${SUITE.teardown.status}    FAIL
    Output should contain teardown error    Expected failure

Erroring Suite Teardown
    Run Tests    ${EMPTY}    core/erroring_suite_teardown.robot
    Check Suite Status    ${SUITE}    FAIL
    ...    Suite teardown failed:\nNo keyword with name 'Non-Existing Keyword' found.\n\n${2 FAIL MSG}
    ...    Test 1    Test 2
    Should Be Equal    ${SUITE.teardown.status}    FAIL
    Output should contain teardown error    No keyword with name 'Non-Existing Keyword' found.

Failing Suite Setup And Teardown
    Run Tests    ${EMPTY}     core/failing_suite_setup_and_teardown.robot
    ${error} =    Catenate    SEPARATOR=
    ...    Suite setup failed:\n
    ...    Setup failure\n
    ...    in two lines\n\n
    ...    Also suite teardown failed:\n
    ...    Teardown failure\n
    ...    in two lines
    Check Suite Status    ${SUITE}    FAIL    ${error}\n\n${2 FAIL MSG}
    ...    Test 1    Test 2
    Should Be Equal    ${SUITE.setup.status}    FAIL
    Should Be Equal    ${SUITE.teardown.status}    FAIL
    Output should contain teardown error    Teardown failure\nin two lines

Failing Higher Level Suite Teardown
    Run Tests    ${EMPTY}    core/failing_suite_teardown_dir
    Check Suite Status    ${SUITE}    FAIL
    ...    Suite teardown failed:\nFailure in top level suite teardown\n\n${12 FAIL MSG}
    ...    PTD Passing    PTD Failing    FTD Passing    FTD Failing    PTD PTD Passing
    ...    PTD PTD Failing    PTD FTD Passing    PTD FTD Failing    FTD PTD Passing
    ...    FTD PTD Failing    FTD FTD Passing    FTD FTD Failing
    Check Suite Status    Passing Teardown Dir    FAIL    ${4 FAIL MSG}
    ...    PTD PTD Passing    PTD PTD Failing    PTD FTD Passing    PTD FTD Failing
    Check Suite Status    Ptd Passing Teardown    FAIL    ${2 FAIL MSG}
    ...    PTD PTD Passing    PTD PTD Failing
    Check Suite Status    Ptd Failing Teardown    FAIL
    ...    Suite teardown failed:\nLeaf suite failed\n\n${2 FAIL MSG}
    ...    PTD FTD Passing    PTD FTD Failing
    Check Suite Status    Failing Teardown Dir    FAIL
    ...    Suite teardown failed:\nFailure in sub suite teardown\n\n${4 FAIL MSG}
    ...    FTD PTD Passing    FTD PTD Failing    FTD FTD Passing    FTD FTD Failing
    Check Suite Status    Ftd Passing Teardown    FAIL    ${2 FAIL MSG}
    ...    FTD PTD Passing    FTD PTD Failing
    Check Suite Status    Ftd Failing Teardown    FAIL
    ...    Suite teardown failed:\nFailure in suite teardown\n\n${2 FAIL MSG}
    ...    FTD FTD Passing    FTD FTD Failing

Failed teardown is noticed when generating only report with Robot
    ${rc} =    Run Tests Without Processing Output
    ...    --report report.html --output NONE    core/failing_suite_teardown.robot
    Should Be Equal As Integers    ${rc}    2

Failed teardown is noticed when generating only report with Rebot
    ${rc} =    Run Tests Without Processing Output
    ...    --report report.html    core/failing_suite_teardown.robot
    Should Be Equal As Integers    ${rc}    2
    ${rc} =    Run Rebot Without Processing Output
    ...    --report report.html --output NONE    ${OUTFILE}
    Should Be Equal As Integers    ${rc}    2

Long Error Messages
    Run Tests    ${EMPTY}    core/long_suite_setup_and_teardown_errors.robot
    ${setup} =    Evaluate    'setup\\n' * 20
    ${teardown} =    Evaluate    'teardown\\n' * 20
    ${explanation} =    Set Variable    [ Message content over the limit has been removed. ]\n
    ${error} =    Catenate    SEPARATOR=\n
    ...    Suite setup failed:
    ...    ${setup}${SPACE * 4}${explanation}${setup}
    ...    Also suite teardown failed:
    ...    ${teardown}${SPACE * 4}${explanation}${teardown}
    ...    ${1 FAIL MSG}
    Check Suite Status    ${SUITE}    FAIL    ${error}    Test

*** Keywords ***
Check Suite Status
    [Arguments]    ${suite or name}    ${status}    ${message}    @{tests}
    ${is string} =    Run Keyword And Return Status    Should Be String    ${suite or name}
    ${suite} =    Run Keyword If    ${is string}    Get Test Suite    ${suite or name}
    ...    ELSE    Set Variable    ${suite or name}
    Should Be Equal    ${suite.status}    ${status}    Wrong suite status
    Should Be Equal    ${suite.full_message}    ${message}    Wrong suite message
    Should Contain Tests    ${suite}    @{tests}

Output should contain teardown error
    [Arguments]    ${error}
    ${keywords} =    Get Elements    ${OUTFILE}    suite/kw
    Element Text Should Be    ${keywords[-1]}    ${error}    xpath=status


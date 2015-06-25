*** Settings ***
Force Tags      regression    pybot  jybot
Resource        atest_resource.robot
Library         ProcessManager.py
Test Teardown   Run Keyword If Test Failed    Log Stdout And Stderr

*** Variables ***
${TEST FILE}    %{TEMPDIR}${/}signal-tests.txt

*** Test Cases ***
SIGINT Signal Should Stop Test Execution Gracefully
    Start And Send Signal  without_any_timeout.robot  One SIGINT
    Process Output For Graceful Shutdown
    Check Test Cases Have Failed Correctly

SIGTERM Signal Should Stop Test Execution Gracefully
    [Tags]  x-exclude-on-windows
    Start And Send Signal  without_any_timeout.robot  One SIGTERM
    Process Output For Graceful Shutdown
    Check Test Cases Have Failed Correctly

Execution Is Stopped Even If Keyword Swallows Exception
    [Documentation]  This only works with Python.
    Run Keyword If    not "${PYTHON}"    Remove Tags    regression
    Start And Send Signal  swallow_exception.robot  One SIGTERM
    Process Output For Graceful Shutdown
    Check Test Cases Have Failed Correctly

One Signal Should Stop Test Execution Gracefully When Run Keyword Is Used
    Start And Send Signal  run_keyword.robot  One SIGTERM
    Process Output For Graceful Shutdown
    Check Test Cases Have Failed Correctly

One Signal Should Stop Test Execution Gracefully When Test Timeout Is Used
    Start And Send Signal  test_timeout.robot  One SIGTERM
    Process Output For Graceful Shutdown
    Check Test Cases Have Failed Correctly

One Signal Should Stop Test Execution Gracefully When Keyword Timeout Is Used
    Start And Send Signal  keyword_timeout.robot  One SIGTERM
    Process Output For Graceful Shutdown
    Check Test Cases Have Failed Correctly

Two SIGINT Signals Should Stop Test Execution Forcefully
    Start And Send Signal  without_any_timeout.robot  Two SIGINTs  2s
    Check Tests Have Been Forced To Shutdown

Two SIGTERM Signals Should Stop Test Execution Forcefully
    [Tags]  x-exclude-on-windows
    Start And Send Signal  without_any_timeout.robot  Two SIGTERMs  2s
    Check Tests Have Been Forced To Shutdown

Two Signals Should Stop Test Execution Forcefully When Run Keyword Is Used
    Start And Send Signal  run_keyword.robot  Two SIGINTs  2s
    Check Tests Have Been Forced To Shutdown

Two Signals Should Stop Test Execution Forcefully When Test Timeout Is Used
    Start And Send Signal  test_timeout.robot  Two SIGINTs  2s
    Check Tests Have Been Forced To Shutdown

Two Signals Should Stop Test Execution Forcefully When Keyword Timeout Is Used
    Start And Send Signal  keyword_timeout.robot  Two SIGINTs  2s
    Check Tests Have Been Forced To Shutdown

One Signal Should Stop Test Execution Gracefully And Test Case And Suite Teardowns Should Be Run
    Start And Send Signal  with_teardown.robot  One SIGINT
    Process Output For Graceful Shutdown
    Check Test Cases Have Failed Correctly
    ${tc} =  Get Test Case  Test
    Check Log Message  ${tc.teardown.msgs[0]}  Logging Test Case Teardown
    ${ts} =  Get Test Suite  With Teardown
    Check Log Message  ${ts.teardown.kws[0].msgs[0]}  Logging Suite Teardown

Skip Teardowns After Stopping Gracefully
    Start And Send Signal  with_teardown.robot  One SIGINT  0s  --SkipTeardownOnExit
    Process Output For Graceful Shutdown
    Check Test Cases Have Failed Correctly
    ${tc} =  Get Test Case  Test
    Should Be Equal  ${tc.teardown}  ${None}
    ${ts} =  Get Test Suite  With Teardown
    Should Be Equal  ${ts.teardown}  ${None}


*** Keywords ***
Start And Send Signal
    [Arguments]    ${datasource}    ${signals}    ${sleep}=0s    @{extra options}
    Remove File    ${TEST FILE}
    Start Run    ${datasource}    ${sleep}    @{extra options}
    Wait Until Created    ${TESTFILE}    timeout=45s
    Run Keyword    ${signals}
    Wait Until Finished

Start Run
    [Arguments]    ${datasource}    ${sleep}    @{extra options}
    Set Runners
    ${datasource} =    Set Variables And Get Datasources    running/stopping_with_signal/${datasource}
    @{runner} =    Get Runner    ${INTERPRETER}    ${ROBOTPATH}
    @{command} =    Create List
    ...    @{runner}
    ...    --output    ${OUTFILE}    --report    NONE    --log    NONE
    ...    --variable    TESTSIGNALFILE:${TEST FILE}
    ...    --variable    TEARDOWNSLEEP:${sleep}
    ...    @{extra options}
    ...    ${datasource}
    Log Many    @{command}
    ProcessManager.start process    @{command}

Check Test Cases Have Failed Correctly
    Check Test Tags    Test
    Check Test Tags    Test2    robot-exit

Check Tests Have Been Forced To Shutdown
    ${stderr} =    ProcessManager.Get Stderr
    Should Contain    ${stderr}    Execution forcefully stopped

Process Output For Graceful Shutdown
    Wait Until Created    ${OUTFILE}    timeout=45s
    Process Output    ${OUTFILE}

One SIGINT
    Send Terminate    SIGINT

One SIGTERM
    Send Terminate    SIGTERM

Two SIGINTs
    One SIGINT
    Sleep    1s
    One SIGINT

Two SIGTERMs
    One SIGTERM
    Sleep    1s
    One SIGTERM

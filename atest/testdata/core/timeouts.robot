*** Settings ***
Documentation   Tests using test case and user keyword timeouts. It seems that on Cygwin Python tests now and then fail with an error message "error: can't allocate lock"
Suite Setup     Clean Up Timeout Temp
Test Timeout    4 seconds
Library         ExampleLibrary
Library         ExampleJavaLibrary
Library         OperatingSystem

*** Variables ***
${TIMEOUT TEMP}    %{TEMPDIR}${/}robot_timeout_tests
${TEST STOPPED}    ${TIMEOUT TEMP}${/}test_stopped.txt
${KW STOPPED}      ${TIMEOUT TEMP}${/}kw_stopped.txt

*** Test Cases ***
Passing
    No Operation

Sleeping But Passing
    Sleep Without Logging  0.1
    Sleep Without Logging  0.1

Failing Before Timeout
    [Documentation]  FAIL Failure before timeout
    Fail  Failure before timeout

Show Correct Trace Back When Failing Before Timeout
    [Documentation]  FAIL Failure before timeout
    [Setup]   Set Log Level   DEBUG
    Fail  Failure before timeout
    [Teardown]   Set Log Level   INFO

Show Correct Trace Back When Failing In Java Before Timeout
    [Documentation]  FAIL ArrayStoreException: This is exception message
    [Setup]   Set Log Level   DEBUG
    java exception    This is exception message
    [Teardown]   Set Log Level   INFO

Sleeping And Timeouting
    [Documentation]  FAIL Test timeout 4 seconds exceeded.
    Sleep Without Logging  10
    Fail  This should not be executed

Total Time Too Long
    [Documentation]  FAIL Test timeout 500 milliseconds exceeded.
    [Timeout]  500 milliseconds
    Sleep Without Logging  0.2
    Sleep Without Logging  0.2
    Sleep Without Logging  0.2
    Fail  This should not be executed

Looping Forever And Timeouting
    [Documentation]  FAIL Test timeout 333 milliseconds exceeded.
    [Timeout]  333 milliseconds
    Loop Forever
    Fail  This should not be executed

Stopped After Test Timeout
    [Documentation]  Keyword that is stopped after test timeout should not write to a file FAIL Test timeout 500 milliseconds exceeded.
    [Timeout]  0.5s
    Write To File After Sleeping  ${TEST STOPPED}  2

Stopped After Keyword Timeout
    [Documentation]  Keyword that is stopped after keyword timeout should not write to a file FAIL Keyword timeout 100 milliseconds exceeded.
    [Timeout]  1 minute
    Timeouted Write To File After Sleeping  ${KW STOPPED}  2

Timout Defined For One Test
    [Documentation]  FAIL Test timeout 42 milliseconds exceeded.
    [Timeout]  42 milliseconds
    Sleep  3

Timeouted Keyword Passes
    [Documentation]  PASS
    Log  Testing outputcapture in timeouted test
    Timeouted Keyword Passes

Timeouted Keyword Fails Before Timeout
    [Documentation]  FAIL Failure before keyword timeout
    [Timeout]  2 seconds
    Timeouted Keyword Fails Before Timeout

Timeouted Keyword Timeouts
    [Documentation]  FAIL Keyword timeout 99 milliseconds exceeded.
    [Timeout]  2 seconds
    Timeouted Keyword Timeouts

Timeouted Keyword Timeouts Due To Total Time
    [Documentation]  FAIL Keyword timeout 1 second exceeded.
    [Timeout]  2 seconds
    Timeouted Keyword Timeouts Due To Total Time

Test Timeouts When Also Keywords Are Timeouted
    [Documentation]  FAIL Test timeout 500 milliseconds exceeded.
    [Timeout]  500 milliseconds
    Timeouted Keyword Passes  0.3
    Timeouted Keyword Passes  0.3

Timeout Format
    [Documentation]  This is thoroughly tested on unit level so here are only some sanity checks FAIL Keyword timeout 1 second exceeded.
    [Timeout]  2 days 4 hours 56 minutes 18 seconds
    Timeout Format

Test Timeout During Setup
    [Documentation]  FAIL Setup failed:\n  Test timeout 1 second exceeded.
    [Timeout]  1 second
    [Setup]  Sleep Without Logging  60
    Fail  This should not be executed

Teardown After Test Timeout
    [Documentation]  FAIL Test timeout 500 milliseconds exceeded.
    [Timeout]  500 milliseconds
    Sleep Without Logging  1s
    [Teardown]  Log  Teardown executed

Failing Teardown After Test Timeout
    [Documentation]  FAIL Test timeout 1 second exceeded.\n  \n  Also teardown failed:\n  Failure before keyword timeout
    [Timeout]  1 second
    Sleep Without Logging  1.1
    [Teardown]  Timeouted Keyword Fails Before Timeout

Teardown With Sleep After Test Timeout
    [Documentation]  FAIL Test timeout 1 second exceeded.
    [Timeout]  1 second
    Sleep Without Logging  1.1
    [Teardown]  Sleep And Log  0.5  Teardown executed

Test Timeout During Teardown
    [Documentation]  FAIL Test timeout 2 seconds exceeded.
    [Timeout]  2 seconds
    Comment  No timeout here
    [Teardown]  Sleep And Log  2.1  Teardown executed

Timeouted Setup Passes
    [Documentation]  PASS
    [Setup]  Timeouted Keyword Passes  0.001
    Timeouted Keyword Passes  0

Timeouted Setup Timeouts
    [Documentation]  FAIL Setup failed:\n  Keyword timeout 99 milliseconds exceeded.
    [Timeout]
    [Setup]  Timeouted Keyword Timeouts
    Fail  This should not be executed

Timeouted Teardown Passes
    [Documentation]  PASS
    [Setup]  Timeouted Keyword Passes  0
    NOOP
    [Teardown]  Timeouted Keyword Passes  0.001

Timeouted Teardown Timeouts
    [Documentation]  FAIL Teardown failed:\n  Keyword timeout 99 milliseconds exceeded.
    [Timeout]
    [Setup]  Timeouted Keyword Passes
    Timeouted Keyword Passes
    [Teardown]  Timeouted Keyword Timeouts

Timeouted UK Using Non Timeouted UK
    [Documentation]  FAIL Keyword timeout 2 seconds exceeded.
    [Timeout]
    Timeouted UK Using Non Timeouted UK

Shortest UK Timeout Should Be Applied
    [Documentation]  FAIL Keyword timeout 2 seconds exceeded.
    [Timeout]
    Timeouted UK Using Timeouted UK

Shortest Test Or UK Timeout Should Be Applied
    [Documentation]  FAIL Test timeout 1 second exceeded.
    [Timeout]  1 second
    Timeouted UK Using Timeouted UK

Timeouted Set Keyword
    [Documentation]  FAIL Keyword timeout 99 milliseconds exceeded.
    ${msg} =  Timeouted Keyword Passes  0.01
    Equals  ${msg}  Slept 0.01s
    ${msg} =  Timeouted Keyword Timeouts
    Fail  This should not be executed

Test Timeout Should Not Be Active For Run Keyword Variants But To Keywords They Execute
    [Documentation]  FAIL Test timeout 100 milliseconds exceeded.
    [Timeout]  100 milliseconds
    Run Keyword  Sleep Without Logging  2

Keyword Timeout Should Not Be Active For Run Keyword Variants But To Keywords They Execute
    [Documentation]  FAIL Keyword timeout 200 milliseconds exceeded.
    Run Keyword With Timeout

It Should Be Possible To Print From Java Libraries When Test Timeout Has Been Set
    ExampleJavaLibrary.Print  My message from java lib

Timeouted Keyword Called With Wrong Number of Arguments
    [Documentation]  FAIL Keyword 'Timeouted Keyword Passes' expected 0 to 1 arguments, got 4.
    Timeouted Keyword Passes  wrong  number  of  arguments
    [Teardown]  No Operation

Timeouted Keyword Called With Wrong Number of Arguments with Run Keyword
    [Documentation]  FAIL Keyword 'Timeouted Keyword Passes' expected 0 to 1 arguments, got 4.
    Run Keyword  Timeouted Keyword Passes  wrong  number  of  arguments
    [Teardown]  No Operation


*** Keywords ***
Clean Up Timeout Temp
    Remove Dir  ${timeout_temp}  recursive
    Create Dir  ${timeout_temp}

Timeouted Keyword Passes
    [Arguments]  ${secs}=0.1
    [Timeout]  5 seconds
    Log  Testing outputcapture in timeouted keyword
    Sleep Without Logging  ${secs}
    [Return]  Slept ${secs}s

Timeouted Keyword Fails Before Timeout
    [Timeout]  5 seconds
    Fail  Failure before keyword timeout

Timeouted Keyword Timeouts
    [Timeout]  99 milliseconds
    Sleep Without Logging  2
    [Return]  Nothing, really

Timeouted Keyword Timeouts Due To Total Time
    [Timeout]  1 second
    Sleep Without Logging  0.3
    Sleep Without Logging  0.3
    Sleep Without Logging  0.3
    Sleep Without Logging  0.3

Timeouted Write To File After Sleeping
    [Arguments]  ${path}  ${secs}
    [Timeout]  100 milliseconds
    Write To File After Sleeping  ${path}  ${secs}
    Fail  This should not be executed

Timeout Format
    [Timeout]  1 second
    Sleep Without Logging  2

Sleep And Log
    [Arguments]  ${secs}  ${msg}
    Sleep Without Logging  ${secs}
    Log  ${msg}

Timeouted UK Using Non Timeouted UK
    [Timeout]  2 seconds
    Non Timeouted UK

Timeouted UK Using Non Timeouted UK 2
    [Timeout]  6 seconds
    Non Timeouted UK

Non Timeouted UK
    Sleep  10

Timeouted UK Using Timeouted UK
    [Timeout]  2 seconds
    Timeouted UK Using Non Timeouted UK 2

Run Keyword With Timeout
    [Timeout]  200 milliseconds
    Run Keyword Unless  False  Log  Hello
    Run Keyword If  True  Sleep  3


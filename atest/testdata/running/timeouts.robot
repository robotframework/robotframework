*** Settings ***
Documentation     Tests using test case and user keyword timeouts.
Suite Setup       Clean Up Timeout Temp
Test Timeout      1 second
Library           ExampleLibrary
Library           OperatingSystem

*** Variables ***
${TIMEOUT TEMP}    %{TEMPDIR}${/}robot_timeout_tests
${TEST STOPPED}    ${TIMEOUT TEMP}${/}test_stopped.txt
${KW STOPPED}      ${TIMEOUT TEMP}${/}kw_stopped.txt

*** Test Cases ***
Passing
    No Operation

Sleeping But Passing
    Sleep Without Logging    0.1
    Sleep Without Logging    0.1

Failing Before Timeout
    [Documentation]    FAIL Failure before timeout
    [Timeout]    2000ms
    Fail    Failure before timeout

Show Correct Trace Back When Failing Before Timeout
    [Documentation]    FAIL Failure before timeout
    Exception    RuntimeError    Failure before timeout

Sleeping And Timeouting
    [Documentation]    FAIL Test timeout 1 second exceeded.
    Sleep Without Logging    5
    Fail    This should not be executed

Total Time Too Long 1
    [Documentation]    FAIL Test timeout 300 milliseconds exceeded.
    [Timeout]    300 milliseconds
    Sleep Without Logging    0.1
    Sleep Without Logging    0.2
    Sleep Without Logging    0.3
    Fail    This should not be executed

Total Time Too Long 2
    [Documentation]    FAIL Test timeout 300 milliseconds exceeded.
    [Timeout]    300 milliseconds
    Sleep Without Logging    0.1
    Sleep Without Logging    0.3
    Fail    This should not be executed

Total Time Too Long 3
    [Documentation]    FAIL Test timeout 100 milliseconds exceeded.
    [Timeout]    0.1
    FOR    ${i}    IN RANGE    1000
        Log    How many kws can we run in 0.1s?
    END
    Fail    This should not be executed

Total Time Too Long 4
    [Documentation]    FAIL Test timeout 100 milliseconds exceeded.
    [Timeout]    0.1
    FOR    ${i}    IN RANGE    1000
        Run Keyword And Expect Error
        ...    How many kws can we run in 0.1s?
        ...    Fail    How many kws can we run in 0.1s?
    END
    Fail    This should not be executed

Looping Forever And Timeouting
    [Documentation]    FAIL Test timeout 123 milliseconds exceeded.
    [Timeout]    123 milliseconds
    Loop Forever
    Fail    This should not be executed

Stopped After Test Timeout
    [Documentation]    Keyword that is stopped after test timeout should not write to a file.
    ...    FAIL Test timeout 200 milliseconds exceeded.
    [Timeout]    0.2s
    Write To File After Sleeping    ${TEST STOPPED}    2

Stopped After Keyword Timeout
    [Documentation]    Keyword that is stopped after keyword timeout should not write to a file.
    ...    FAIL Keyword timeout 200 milliseconds exceeded.
    [Timeout]    1 minute
    Timeouted Write To File After Sleeping    ${KW STOPPED}    2

Timout Defined For One Test
    [Documentation]    FAIL Test timeout 42 milliseconds exceeded.
    [Timeout]    42 milliseconds
    Sleep    3

Timeouted Keyword Passes
    [Timeout]    1 day
    Log    Testing logging in timeouted test
    Timeouted Keyword Passes

Timeouted Keyword Fails Before Timeout
    [Documentation]    FAIL Failure before keyword timeout
    [Timeout]    2 days
    Timeouted Keyword Fails Before Timeout

Timeouted Keyword Timeouts
    [Documentation]    FAIL Keyword timeout 99 milliseconds exceeded.
    [Timeout]    2 seconds
    Timeouted Keyword Timeouts

Timeouted Keyword Timeouts Due To Total Time
    [Documentation]    FAIL Keyword timeout 300 milliseconds exceeded.
    [Timeout]    2 seconds
    Timeouted Keyword Timeouts Due To Total Time

Test Timeouts When Also Keywords Are Timeouted
    [Documentation]    FAIL Test timeout 300 milliseconds exceeded.
    [Timeout]    300 milliseconds
    Timeouted Keyword Passes    0.2
    Timeouted Keyword Passes    0.2
    Timeouted Keyword Passes    0.2

Keyword Timeout From Variable
    [Documentation]    FAIL Keyword timeout 1 millisecond exceeded.
    Keyword timeout from variable

Keyword Timeout From Argument
    [Documentation]    FAIL Keyword timeout 2 milliseconds exceeded.
    Keyword timeout from argument   1s
    Keyword timeout from argument   0.002

Embedded Arguments Timeout From Argument
    [Documentation]    FAIL Keyword timeout 3 milliseconds exceeded.
    Embedded args timeout '1 second' from arguments
    Embedded args timeout '0.003' from arguments

Local Variables Are Not Visible In Child Keyword Timeout
    [Documentation]    FAIL Setting keyword timeout failed: Variable '\${local}' not found.
    ${local}=    Set variable    1 day
    Keyword that uses parent local variable for timeout

Timeout Format
    [Documentation]    This is thoroughly tested on unit level so here are only some sanity checks
    ...    FAIL Keyword timeout 1 second exceeded.
    [Timeout]    2 days 4 hours 56 minutes 18 seconds
    Timeout Format

Test Timeout During Setup
    [Documentation]    FAIL Setup failed:
    ...    Test timeout 100 milliseconds exceeded.
    [Setup]    Sleep Without Logging    60
    [Timeout]    0.1 seconds
    Fail    This should not be executed

Teardown After Test Timeout
    [Documentation]    FAIL Test timeout 123 milliseconds exceeded.
    [Timeout]    123 milliseconds
    Sleep Without Logging    1s
    [Teardown]    Log    Teardown executed

Failing Teardown After Test Timeout
    [Documentation]    FAIL Test timeout 100 milliseconds exceeded.
    ...
    ...    Also teardown failed:
    ...    Failure before keyword timeout
    [Timeout]    0.1 second
    Sleep Without Logging    1
    [Teardown]    Timeouted Keyword Fails Before Timeout

Teardown With Sleep After Test Timeout
    [Documentation]    FAIL Test timeout 100 milliseconds exceeded.
    [Timeout]    100 ms
    Sleep Without Logging    1
    [Teardown]    Sleep And Log    0.5    Teardown executed

Test Timeout During Teardown
    [Documentation]    FAIL Test timeout 100 milliseconds exceeded.
    [Timeout]    0.1 seconds
    Comment    No timeout here
    [Teardown]    Sleep And Log    0.5    Teardown executed

Timeouted Setup Passes
    [Setup]    Timeouted Keyword Passes    0.001
    Timeouted Keyword Passes    0

Timeouted Setup Timeouts
    [Documentation]    FAIL Setup failed:
    ...    Keyword timeout 99 milliseconds exceeded.
    [Setup]    Timeouted Keyword Timeouts
    [Timeout]
    Fail    This should not be executed

Timeouted Teardown Passes
    [Setup]    Timeouted Keyword Passes    0
    No Operation
    [Teardown]    Timeouted Keyword Passes    0.001

Timeouted Teardown Timeouts
    [Documentation]    FAIL Teardown failed:
    ...    Keyword timeout 99 milliseconds exceeded.
    [Setup]    Timeouted Keyword Passes
    [Timeout]
    Timeouted Keyword Passes
    [Teardown]    Timeouted Keyword Timeouts

Timeouted UK Using Non Timeouted UK
    [Documentation]    FAIL Keyword timeout 222 milliseconds exceeded.
    [Timeout]
    Timeouted UK Using Non Timeouted UK

Shortest UK Timeout Should Be Applied
    [Documentation]    FAIL Keyword timeout 200 milliseconds exceeded.
    [Timeout]
    Timeouted UK Using Timeouted UK

Shortest Test Or UK Timeout Should Be Applied
    [Documentation]    FAIL Test timeout 100 milliseconds exceeded.
    [Timeout]    0.1 second
    Timeouted UK Using Timeouted UK

Timeouted Set Keyword
    [Documentation]    FAIL Keyword timeout 99 milliseconds exceeded.
    ${msg} =    Timeouted Keyword Passes    0.01
    Should Be Equal    ${msg}    Slept 0.01s
    ${msg} =    Timeouted Keyword Timeouts
    Fail    This should not be executed

Test Timeout Should Not Be Active For Run Keyword Variants But To Keywords They Execute
    [Documentation]    FAIL Test timeout 100 milliseconds exceeded.
    [Timeout]    100 milliseconds
    Run Keyword    Sleep Without Logging    2

Keyword Timeout Should Not Be Active For Run Keyword Variants But To Keywords They Execute
    [Documentation]    FAIL Keyword timeout 200 milliseconds exceeded.
    Run Keyword With Timeout

Timeouted Keyword Called With Wrong Number of Arguments
    [Documentation]    FAIL Keyword 'Timeouted Keyword Passes' expected 0 to 1 arguments, got 4.
    Timeouted Keyword Passes    wrong    number    of    arguments
    [Teardown]    No Operation

Timeouted Keyword Called With Wrong Number of Arguments with Run Keyword
    [Documentation]    FAIL Keyword 'Timeouted Keyword Passes' expected 0 to 1 arguments, got 4.
    Run Keyword    Timeouted Keyword Passes    wrong    number    of    arguments
    [Teardown]    No Operation

Zero timeout is ignored
    [Timeout]    0
    Zero timeout is ignored

Negative timeout is ignored
    [Timeout]    -1
    Negative timeout is ignored

Invalid test timeout
    [Documentation]    FAIL Setting test timeout failed: Invalid time string '¡Bäng!'.
    [Timeout]    ¡Bäng!
    Fail    Should not be executed!

Invalid keyword timeout
    [Documentation]    FAIL Setting keyword timeout failed: Invalid time string '¡Bäng!'.
    Invalid keyword timeout

*** Keywords ***
Clean Up Timeout Temp
    Remove Directory    ${timeout_temp}    recursive
    Create Directory    ${timeout_temp}

Timeouted Keyword Passes
    [Arguments]    ${secs}=0.1
    [Timeout]    5 seconds
    Log    Testing logging in timeouted keyword
    Sleep Without Logging    ${secs}
    [Return]    Slept ${secs}s

Timeouted Keyword Fails Before Timeout
    [Timeout]    9000
    Fail    Failure before keyword timeout

Timeouted Keyword Timeouts
    [Timeout]    99 milliseconds
    Sleep Without Logging    2
    [Return]    Nothing, really

Timeouted Keyword Timeouts Due To Total Time
    [Timeout]    0.3 seconds
    Sleep Without Logging    0.1
    Sleep Without Logging    0.1
    Sleep Without Logging    0.1
    Sleep Without Logging    0.1
    Sleep Without Logging    0.1

Timeouted Write To File After Sleeping
    [Arguments]    ${path}    ${secs}
    [Timeout]    200 milliseconds
    Write To File After Sleeping    ${path}    ${secs}
    Fail    This should not be executed

Timeout Format
    [Timeout]    1 second
    Sleep Without Logging    2

Sleep And Log
    [Arguments]    ${secs}    ${msg}
    Sleep Without Logging    ${secs}
    Log    ${msg}

Timeouted UK Using Non Timeouted UK
    [Timeout]    0.222
    Non Timeouted UK

Timeouted UK Using Non Timeouted UK 2
    [Timeout]    6 seconds
    Non Timeouted UK

Non Timeouted UK
    Sleep    10

Timeouted UK Using Timeouted UK
    [Timeout]    0.2 seconds
    Timeouted UK Using Non Timeouted UK 2

Run Keyword With Timeout
    [Timeout]    200 milliseconds
    Run Keyword Unless    False    Log    Hello
    Run Keyword If    True    Sleep    3

Keyword timeout from variable
    [Timeout]    ${0.001}
    Sleep    0.1

Keyword timeout from argument
    [Arguments]   ${timeout}
    [Timeout]    ${timeout}
    Sleep    0.1

Embedded args timeout '${timeout}' from arguments
    [Timeout]    ${timeout}
    Sleep    0.1

Keyword that uses parent local variable for timeout
    [Timeout]    ${local}
    Sleep    0.1

Zero timeout is ignored
    [Timeout]    0
    Sleep    0.1

Negative timeout is ignored
    [Timeout]    -1
    Sleep    0.1

Invalid keyword timeout
    [Timeout]    ¡Bäng!
    No Operation

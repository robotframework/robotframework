*** Settings ***
Suite Setup     Run Tests  ${EMPTY}  core/timeouts.robot
Suite Teardown  Remove Directory  ${TIMEOUT TEMP}  recursive
Resource        atest_resource.robot

*** Variables ***
${TIMEOUT TEMP}  %{TEMPDIR}${/}robot_timeout_tests
${TEST STOPPED}  ${TIMEOUT TEMP}${/}test_stopped.txt
${KW STOPPED}    ${TIMEOUT TEMP}${/}kw_stopped.txt

*** Test Cases ***
Timeouted Test Passes
    Check Test Case    Passing
    Check Test Case    Sleeping But Passing

Timeouted Test Fails Before Timeout
    Check Test Case    Failing Before Timeout

Show Correct Trace Back When Failing Before Timeout
    [Tags]    no-ipy    # For some reason IronPython loses the traceback in this case.
    ${tc} =   Check Test Case    ${TEST NAME}
    ${expected} =    Catenate    SEPARATOR=\n
    ...    Traceback (most recent call last):
    ...    ${SPACE*2}File "*", line *, in exception
    ...    ${SPACE*4}raise exception(msg)
    Check Log Message    ${tc.kws[0].msgs[-1]}    ${expected}    pattern=yes    level=DEBUG

Show Correct Trace Back When Failing In Java Before Timeout
    [tags]  require-jython
    ${tc} =   Check Test Case    ${TEST NAME}
    Should Contain    ${tc.kws[0].msgs[-1].message}    at ExampleJavaLibrary.exception(

Timeouted Test Timeouts
    Check Test Case    Sleeping And Timeouting
    Check Test Case    Total Time Too Long
    Check Test Case    Looping Forever And Timeouting

Timout Defined For One Test
    Check Test Case    ${TEST NAME}

Stopped After Test Timeout
    Check Test Case    ${TEST NAME}
    File Should Be Empty  ${TEST STOPPED}

Timeouted Keyword Passes
    Check Test Case    ${TEST NAME}

Timeouted Keyword Fails Before Timeout
    Check Test Case    ${TEST NAME}

Timeouted Keyword Timeouts
    Check Test Case    ${TEST NAME}

Timeouted Keyword Timeouts Due To Total Time
    Check Test Case    ${TEST NAME}

Stopped After Keyword Timeout
    Check Test Case    ${TEST NAME}
    File Should Be Empty  ${KW STOPPED}

Test Timeouts When Also Keywords Are Timeouted
    Check Test Case    ${TEST NAME}

Timeout Format
    ${tc} =   Check Test Case    ${TEST NAME}
    Should Be Equal    ${tc.timeout}    2 days 4 hours 56 minutes 18 seconds

Test Timeout During Setup
    Check Test Case    ${TEST NAME}

Teardown After Test Timeout
    [Documentation]  Test that teardown is executed after a test has timed out
    ${tc} =   Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.teardown.msgs[0]}    Teardown executed
    ${tc} =  Check Test Case    Teardown With Sleep After Test Timeout
    Check Log Message    ${tc.teardown.kws[1].msgs[0]}    Teardown executed

Failing Teardown After Test Timeout
    Check Test Case    ${TEST NAME}

Test Timeout During Teardown
    [Documentation]  Test timeout should not interrupt teardown but test should be failed afterwards
    ${tc} =   Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.teardown.kws[1].msgs[0]}    Teardown executed

Timeouted Setup Passes
    Check Test Case    ${TEST NAME}

Timeouted Setup Timeouts
    Check Test Case    ${TEST NAME}

Timeouted Teardown Passes
    Check Test Case    ${TEST NAME}

Timeouted Teardown Timeouts
    Check Test Case    ${TEST NAME}

Timeouted UK Using Non Timeouted UK
    Check Test Case    ${TEST NAME}

Shortest UK Timeout Should Be Applied
    Check Test Case    ${TEST NAME}

Shortest Test Or UK Timeout Should Be Applied
    Check Test Case    ${TEST NAME}

Timeouted Set Keyword
    Check Test Case    ${TEST NAME}

Test Timeout Should Not Be Active For Run Keyword Variants But To Keywords They Execute
    Check Test Case    ${TEST NAME}

Keyword Timeout Should Not Be Active For Run Keyword Variants But To Keywords They Execute
    Check Test Case    ${TEST NAME}

Output Capture With Timeouts
    [Documentation]  Testing that capturing output works with timeouts
    ${tc} =    Check Test Case    Timeouted Keyword Passes
    Check Log Message    ${tc.kws[0].msgs[0]}    Testing outputcapture in timeouted test
    Check Log Message    ${tc.kws[1].kws[0].msgs[0]}    Testing outputcapture in timeouted keyword

It Should Be Possible To Print From Java Libraries When Test Timeout Has Been Set
    [Tags]  require-jython
    ${tc} =   Check Test Case    ${TEST NAME}
    Check Log message    ${tc.kws[0].msgs[0]}    My message from java lib

Timeouted Keyword Called With Wrong Number of Arguments
    Check Test Case  ${TEST NAME}

Timeouted Keyword Called With Wrong Number of Arguments with Run Keyword
    Check Test Case  ${TEST NAME}

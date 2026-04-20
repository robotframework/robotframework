*** Settings ***
Documentation     Simplified tests for Global Execution Timeout (`--timeout`).
Resource          atest_resource.robot

*** Variables ***
${FAIL_1S}        Total Execution timeout 1 second exceeded.

*** Test Cases ***
Basic Global Timeout
    [Documentation]    Global timeout (1s) triggers when a test sleeps for 2s.
    Run Tests    --timeout 1s --test "Long Sleep"    running/global_timeout/basic.robot
    Check Test Case    Long Sleep

Global Timeout Wins Over Longer Test Timeout
    [Documentation]    Global timeout (1s) overrides a longer [Timeout] (5s) on the test.
    Run Tests    --timeout 1s --test "Global Timeout Wins Over Longer Test Timeout"    running/global_timeout/keyword_timeout.robot
    Check Test Case    Global Timeout Wins Over Longer Test Timeout

Shorter Test Timeout Wins Over Global Timeout
    [Documentation]    A shorter [Timeout] (0.5s) on the test overrides the global timeout (2s).
    Run Tests    --timeout 2s --test "Shorter Test Timeout Wins Over Global Timeout"    running/global_timeout/keyword_timeout.robot
    Check Test Case    Shorter Test Timeout Wins Over Global Timeout

Cumulative Global Timeout
    [Documentation]    Global timeout is cumulative across tests. 0.1s + 2s fails at total 1s limit.
    Run Tests    --timeout 1s --test "Short Sleep" --test "Long Sleep"    running/global_timeout/basic.robot
    Check Test Case    Short Sleep
    Check Test Case    Long Sleep

Global Timeout In Test Teardown
    [Documentation]    Global timeout triggers during test teardown.
    Run Tests    --timeout 1s --test "Timeout In Test Teardown"    running/global_timeout/test_teardown.robot
    Check Test Case    Timeout In Test Teardown

Global Timeout Wins Over Longer Keyword Timeout
    [Documentation]    Global timeout (1s) overrides a longer [Timeout] (10s) on a keyword.
    Run Tests    --timeout 1s --test "Global Timeout Wins Over Longer Keyword Timeout"    running/global_timeout/keyword_timeout.robot
    Check Test Case    Global Timeout Wins Over Longer Keyword Timeout

Shorter Keyword Timeout Wins Over Global Timeout
    [Documentation]    A shorter [Timeout] (0.5s) on a keyword overrides the global timeout (2s).
    Run Tests    --timeout 2s --test "Shorter Keyword Timeout Wins Over Global Timeout"    running/global_timeout/keyword_timeout.robot
    Check Test Case    Shorter Keyword Timeout Wins Over Global Timeout

Global Timeout In Suite Teardown
    [Documentation]    Global timeout triggers during suite teardown.
    Run Tests    --timeout 1s --test "Timeout In Suite Teardown"    running/global_timeout/suite_teardown.robot
    ${suite} =    Get Test Suite    Suite Teardown
    Should Be Equal    ${suite.status}    FAIL
    Should Match    ${suite.full_message}    Suite teardown failed:\n${FAIL_1S}\n*

Global Timeout [ ERROR ] Message
    [Documentation]    Console error message check.
    Run Tests    --timeout 1s --test "Long Sleep"    running/global_timeout/basic.robot
    Stderr Should Contain    [ ERROR ] Execution stopped: Total execution timeout of 1 second exceeded.

Invalid Timeout CLI Error
    [Documentation]    Strict CLI validation check.
    Run Tests Without Processing Output    --timeout 10unknown    running/global_timeout/basic.robot
    Stderr Should Contain    Invalid value for option '--timeout': Invalid time string '10unknown'.

Negative Timeout CLI Error
    [Documentation]    Negative CLI timeout check.
    Run Tests Without Processing Output    --timeout -5s    running/global_timeout/basic.robot
    Stderr Should Contain    Invalid value for option '--timeout': Timeout must be positive.

Global Timeout In Suite Setup
    [Documentation]    Global timeout triggers during suite setup.
    Run Tests    --timeout 1s --test "Timeout In Suite Setup"    running/global_timeout/suite_setup.robot
    ${suite} =    Get Test Suite    Suite Setup
    Should Be Equal    ${suite.status}    FAIL
    Should Match    ${suite.full_message}    Suite setup failed:\n${FAIL_1S}\n*

Global Timeout In Nested Suites
    [Documentation]    Hierarchy traversal check.
    Run Tests    --timeout 1s    running/global_timeout/nested/sub/test.robot
    Check Test Case    Test in Sub-Suite

Global Timeout In Dry Run
    [Documentation]    Compatibility with --dryrun.
    Run Tests    --timeout 1s --dryrun --test "Short Sleep"    running/global_timeout/basic.robot
    Check Test Case    Short Sleep

Global Timeout with Variables
    [Documentation]    Support for variables in the --timeout argument itself.
    Run Tests    --variable MY_TIME:1s --timeout \${MY_TIME} --test "Long Sleep"    running/global_timeout/basic.robot
    Check Test Case    Long Sleep

Global Timeout with ExitOnFailure
    [Documentation]    Compatibility with --exitonfailure.
    Run Tests    --timeout 1s --exitonfailure --test "Long Sleep"    running/global_timeout/basic.robot
    Check Test Case    Long Sleep

Global Timeout Via Listener
    [Documentation]    Verify listener can set global timeout (0.1s) that overrides test timeout (default or none).
    Run Tests    --listener TimeoutListener:0.1s --test "Long Sleep"    running/global_timeout/basic.robot
    Check Test Case    Long Sleep    FAIL    Total Execution timeout 100 milliseconds exceeded.

Increase Timeout Via Listener
    [Documentation]    Verify listener can INCREASE global timeout (0.5s -> 3s) allowing a 2s test to pass.
    Run Tests    --timeout 0.5s --listener TimeoutIncreaseListener:3s --test "Long Sleep"    running/global_timeout/basic.robot
    Check Test Case    Long Sleep    PASS    ${EMPTY}
    Stdout Should Contain    DEBUG: Timeout before: 500 milliseconds
    Stdout Should Contain    DEBUG: Timeout after: 3 seconds

Decrease Timeout Via Listener
    [Documentation]    Verify listener can DECREASE global timeout (3s -> 0.1s) causing a 2s test to fail.
    Run Tests    --timeout 3s --listener TimeoutIncreaseListener:0.1s --test "Long Sleep"    running/global_timeout/basic.robot
    Check Test Case    Long Sleep    FAIL    Total Execution timeout 100 milliseconds exceeded.
    Stdout Should Contain    DEBUG: Timeout before: 3 seconds
    Stdout Should Contain    DEBUG: Timeout after: 100 milliseconds

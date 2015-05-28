*** Settings ***
Force Tags        pybot    jybot    regression
Resource          atest_resource.robot

*** Variables ***
${EXIT ON FAILURE}          Critical failure occurred and exit-on-failure mode is in use.

*** Test Cases ***
Exit On Failure
    [Setup]    Run Tests    --exitonfailure    misc/pass_and_fail.robot    misc/suites    running/fatal_exception/02__irrelevant.robot
    Check Test Case    Pass
    Check Test Case    Fail
    Check Test Case    SubSuite1 First    FAIL    ${EXIT ON FAILURE}
    Check Test Case    Suite3 First    FAIL    ${EXIT ON FAILURE}

Imports Are Skipped On Exit
    Previous test should have passed    Exit On Failure
    Should be empty    ${ERRORS.messages}

Correct Suite Teardown Is Executed When ExitOnFailure Is Used
    [Setup]    Run Tests    --exitonfailure    misc/suites
    ${tsuite} =    Get Test Suite    Suites
    Should Be Equal    ${tsuite.teardown.name}    BuiltIn.Log
    ${tsuite} =    Get Test Suite    Fourth
    Should Be Equal    ${tsuite.teardown.name}    BuiltIn.Log
    ${tsuite} =    Get Test Suite    Tsuite3
    Should Be Equal    ${tsuite.teardown}    ${None}

Exit On Failure With Skip Teardown On Exit
    [Setup]    Run Tests    --ExitOnFailure --SkipTeardownOnExit    misc/suites
    ${tcase} =    Check Test Case    Suite4 First
    Should Be Equal    ${tcase.teardown}    ${None}
    ${tsuite} =    Get Test Suite    Fourth
    Should Be Equal    ${tsuite.teardown}    ${None}
    Check Test Case    SubSuite1 First    FAIL    ${EXIT ON FAILURE}
    Check Test Case    Suite3 First    FAIL    ${EXIT ON FAILURE}

Test setup fails
    [Setup]    Run Tests    --ExitOnFail    misc/setups_and_teardowns.robot
    Check Test Case    Test with setup and teardown
    Check Test Case    Test with failing setup
    Check Test Case    Test with failing teardown            FAIL    ${EXIT ON FAILURE}
    Check Test Case    Failing test with failing teardown    FAIL    ${EXIT ON FAILURE}

Test teardown fails
    [Setup]    Run Tests    --ExitOnFail --variable TEST_TEARDOWN:NonExistingKeyword    misc/setups_and_teardowns.robot
    Check Test Case    Test with setup and teardown          FAIL    Teardown failed:\nNo keyword with name 'NonExistingKeyword' found.
    Check Test Case    Test with failing setup               FAIL    ${EXIT ON FAILURE}
    Check Test Case    Test with failing teardown            FAIL    ${EXIT ON FAILURE}
    Check Test Case    Failing test with failing teardown    FAIL    ${EXIT ON FAILURE}

Suite setup fails
    [Setup]    Run Tests    --ExitOnFail --variable SUITE_SETUP:Fail    misc/setups_and_teardowns.robot    misc/pass_and_fail.robot
    Check Test Case    Test with setup and teardown          FAIL    Parent suite setup failed:\nAssertionError
    Check Test Case    Test with failing setup               FAIL    ${EXIT ON FAILURE}
    Check Test Case    Test with failing teardown            FAIL    ${EXIT ON FAILURE}
    Check Test Case    Failing test with failing teardown    FAIL    ${EXIT ON FAILURE}
    Check Test Case    Pass                                  FAIL    ${EXIT ON FAILURE}
    Check Test Case    Fail                                  FAIL    ${EXIT ON FAILURE}

Suite teardown fails
    [Setup]    Run Tests    --ExitOnFail --variable SUITE_TEARDOWN:Fail --test TestWithSetupAndTeardown --test Pass --test Fail
    ...    misc/setups_and_teardowns.robot    misc/pass_and_fail.robot
    Check Test Case    Test with setup and teardown          FAIL    Parent suite teardown failed:\nAssertionError
    Check Test Case    Pass                                  FAIL    ${EXIT ON FAILURE}
    Check Test Case    Fail                                  FAIL    ${EXIT ON FAILURE}

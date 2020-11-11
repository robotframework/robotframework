*** Settings ***
Suite Setup       Run Tests
...               --exitonfailure --skiponfailure skip-on-failure
...               cli/runner/exit_on_failure.robot misc/suites running/fatal_exception/02__irrelevant.robot
Resource          atest_resource.robot

*** Variables ***
${EXIT ON FAILURE}          Failure occurred and exit-on-failure mode is in use.

*** Test Cases ***
Passing tests do not initiate exit-on-failure
    Check Test Case    Passing
    Check Test Case    Passing tests do not initiate exit-on-failure

Skip-on-failure tests do not initiate exit-on-failure
    Check Test Case    Skipped on failure

Failing tests initiate exit-on-failure
    Check Test Case    Failing
    Test Should Have Been Skipped    Not executed

Tests in subsequent suites are skipped
    Test Should Have Been Skipped    SubSuite1 First
    Test Should Have Been Skipped    Suite3 First

Imports in subsequent suites are skipped
    Should Be Equal    ${SUITE.suites[-1].name}    Irrelevant
    Should Be Empty    ${ERRORS.messages}

Correct Suite Teardown Is Executed When ExitOnFailure Is Used
    [Setup]    Run Tests    -X    misc/suites
    ${tsuite} =    Get Test Suite    Suites
    Should Be Equal    ${tsuite.teardown.name}    BuiltIn.Log
    ${tsuite} =    Get Test Suite    Fourth
    Should Be Equal    ${tsuite.teardown.name}    BuiltIn.Log
    ${tsuite} =    Get Test Suite    Tsuite3
    Teardown Should Not Be Defined    ${tsuite}

Exit On Failure With Skip Teardown On Exit
    [Setup]    Run Tests    --ExitOnFailure --SkipTeardownOnExit    misc/suites
    ${tcase} =    Check Test Case    Suite4 First
    Teardown Should Not Be Defined    ${tcase}
    ${tsuite} =    Get Test Suite    Fourth
    Teardown Should Not Be Defined    ${tsuite}
    Test Should Have Been Skipped    SubSuite1 First
    Test Should Have Been Skipped    Suite3 First

Test setup fails
    [Setup]    Run Tests    -X    misc/setups_and_teardowns.robot
    Check Test Case    Test with setup and teardown
    Check Test Case    Test with failing setup
    Test Should Have Been Skipped    Test with failing teardown
    Test Should Have Been Skipped    Failing test with failing teardown

Test teardown fails
    [Setup]    Run Tests
    ...    --ExitOnFail --variable TEST_TEARDOWN:NonExistingKeyword
    ...    misc/setups_and_teardowns.robot
    Check Test Case    Test with setup and teardown    FAIL    Teardown failed:\nNo keyword with name 'NonExistingKeyword' found.
    Test Should Have Been Skipped    Test with failing setup
    Test Should Have Been Skipped    Test with failing teardown
    Test Should Have Been Skipped    Failing test with failing teardown

Suite setup fails
    [Setup]    Run Tests
    ...    --ExitOnFail --variable SUITE_SETUP:Fail
    ...    misc/setups_and_teardowns.robot misc/pass_and_fail.robot
    Test Should Have Been Skipped    Test with setup and teardown
    Test Should Have Been Skipped    Test with failing setup
    Test Should Have Been Skipped    Test with failing teardown
    Test Should Have Been Skipped    Failing test with failing teardown
    Test Should Have Been Skipped    Pass
    Test Should Have Been Skipped    Fail

Suite teardown fails
    [Setup]    Run Tests
    ...    --ExitOnFail --variable SUITE_TEARDOWN:Fail --test TestWithSetupAndTeardown --test Pass --test Fail
    ...    misc/setups_and_teardowns.robot misc/pass_and_fail.robot
    Check Test Case    Test with setup and teardown    FAIL    Parent suite teardown failed:\nAssertionError
    Test Should Have Been Skipped    Pass
    Test Should Have Been Skipped    Fail

*** Keywords ***
Test Should Have Been Skipped
    [Arguments]    ${name}
    ${tc} =    Check Test Case    ${name}    FAIL    ${EXIT ON FAILURE}
    Should Contain    ${tc.tags}    robot:exit

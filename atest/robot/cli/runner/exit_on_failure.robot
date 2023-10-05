*** Settings ***
Suite Setup       Run Tests
...               --exitonfailure --skiponfailure skip-on-failure
...               cli/runner/exit_on_failure.robot misc/suites running/fatal_exception/02__irrelevant.robot
Resource          atest_resource.robot

*** Variables ***
${EXIT ON FAILURE}          Failure occurred and exit-on-failure mode is in use.

*** Test Cases ***
Passing test does not initiate exit-on-failure
    Check Test Case    ${TEST NAME}

Skipped test does not initiate exit-on-failure
    Check Test Case    ${TEST NAME}

Test skipped in teardown does not initiate exit-on-failure
    Check Test Case    ${TEST NAME}

Skip-on-failure test does not initiate exit-on-failure
    Check Test Case    ${TEST NAME}

Test skipped-on-failure in teardown does not initiate exit-on-failure
    Check Test Case    ${TEST NAME}

Failing test initiates exit-on-failure
    Check Test Case    ${TEST NAME}
    Test Should Not Have Been Run    Not executed

Tests in subsequent suites are skipped
    Test Should Not Have Been Run    SubSuite1 First
    Test Should Not Have Been Run    Suite3 First

Imports in subsequent suites are skipped
    Should Be Equal    ${SUITE.suites[-1].name}    Irrelevant
    Should Be Empty    ${ERRORS.messages}

Correct Suite Teardown Is Executed When ExitOnFailure Is Used
    [Setup]    Run Tests    -X    misc/suites
    ${tsuite} =    Get Test Suite    Suites
    Should Be Equal    ${tsuite.teardown.full_name}    BuiltIn.Log
    ${tsuite} =    Get Test Suite    Fourth
    Should Be Equal    ${tsuite.teardown.full_name}    BuiltIn.Log
    ${tsuite} =    Get Test Suite    Tsuite3
    Teardown Should Not Be Defined    ${tsuite}

Exit On Failure With Skip Teardown On Exit
    [Setup]    Run Tests    --ExitOnFailure --SkipTeardownOnExit    misc/suites
    ${tcase} =    Check Test Case    Suite4 First
    Teardown Should Not Be Defined    ${tcase}
    ${tsuite} =    Get Test Suite    Fourth
    Teardown Should Not Be Defined    ${tsuite}
    Test Should Not Have Been Run    SubSuite1 First
    Test Should Not Have Been Run    Suite3 First

Test setup fails
    [Setup]    Run Tests    -X    misc/setups_and_teardowns.robot
    Check Test Case    Test with setup and teardown
    Check Test Case    Test with failing setup
    Test Should Not Have Been Run    Test with failing teardown
    Test Should Not Have Been Run    Failing test with failing teardown

Test teardown fails
    [Setup]    Run Tests
    ...    --ExitOnFail --variable TEST_TEARDOWN:NonExistingKeyword
    ...    misc/setups_and_teardowns.robot
    Check Test Case    Test with setup and teardown    FAIL    Teardown failed:\nNo keyword with name 'NonExistingKeyword' found.
    Test Should Not Have Been Run    Test with failing setup
    Test Should Not Have Been Run    Test with failing teardown
    Test Should Not Have Been Run    Failing test with failing teardown

Suite setup fails
    [Setup]    Run Tests
    ...    --ExitOnFail --variable SUITE_SETUP:Fail
    ...    misc/setups_and_teardowns.robot misc/pass_and_fail.robot
    Test Should Not Have Been Run    Test with setup and teardown
    Test Should Not Have Been Run    Test with failing setup
    Test Should Not Have Been Run    Test with failing teardown
    Test Should Not Have Been Run    Failing test with failing teardown
    Test Should Not Have Been Run    Pass
    Test Should Not Have Been Run    Fail

Suite teardown fails
    [Setup]    Run Tests
    ...    --ExitOnFail --variable SUITE_TEARDOWN:Fail --test TestWithSetupAndTeardown --test Pass --test Fail
    ...    misc/setups_and_teardowns.robot misc/pass_and_fail.robot
    Check Test Case    Test with setup and teardown    FAIL    Parent suite teardown failed:\nAssertionError
    Test Should Not Have Been Run    Pass
    Test Should Not Have Been Run    Fail

Failure set by listener can initiate exit-on-failure
    [Setup]    Run Tests
    ...    --ExitOnFailure --Listener ${DATADIR}/cli/runner/failtests.py
    ...    misc/pass_and_fail.robot
    Check Test Case    Pass    status=FAIL
    Test Should Not Have Been Run    Fail

*** Keywords ***
Test Should Not Have Been Run
    [Arguments]    ${name}
    ${tc} =    Check Test Case    ${name}    FAIL    ${EXIT ON FAILURE}
    Should Contain    ${tc.tags}    robot:exit

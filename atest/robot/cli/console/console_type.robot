*** Settings ***
Resource          console_resource.robot

*** Test Cases ***
Verbose
    Run and verify tests    --console verbose
    Stdout Should Be    warnings_and_errors_stdout.txt
    Stderr Should Be    warnings_and_errors_stderr.txt

Dotted
    Run and verify tests    --Console Dotted
    Stdout Should Be    warnings_and_errors_stdout_dotted.txt
    Stderr Should Be    warnings_and_errors_stderr.txt

Dotted with width
    Run tests    --Console dotted --ConsoleWidth 10    misc/suites misc/suites
    Stdout Should Be    warnings_and_errors_stdout_dotted_10.txt
    Stderr Should Be    empty.txt

Quiet
    Run and verify tests    --ConSole=QuiEt
    Stdout Should Be    empty.txt
    Stderr Should Be    warnings_and_errors_stderr.txt

None
    Run and verify tests    --CONSOLE NONE
    Stdout Should Be    empty.txt
    Stderr Should Be    empty.txt

Invalid
    Run Tests Without Processing Output    --Console Invalid    misc/pass_and_fail.robot
    Stderr Should Be Equal To    [ ERROR ] Invalid console output type 'Invalid'. Available 'VERBOSE', 'DOTTED', 'QUIET' and 'NONE'.${USAGE TIP}\n

--dotted
    Run and verify tests    --dotted
    Stdout Should Be    warnings_and_errors_stdout_dotted.txt
    Stderr Should Be    warnings_and_errors_stderr.txt

--dotted with --rpa
    Run and verify tests    --dotted --rpa
    Stdout Should Be    warnings_and_errors_stdout_dotted.txt    tests=tasks
    Stderr Should Be    warnings_and_errors_stderr.txt

--quiet
    Run and verify tests    --Quiet
    Stdout Should Be    empty.txt
    Stderr Should Be    warnings_and_errors_stderr.txt

Dotted does not show details for skipped
    Run tests    -.    running/fatal_exception
    Stdout Should Be    dotted_fatal_error.txt
    Stderr Should Be    empty.txt

--Dotted --ExitOnFailure
    Run tests    --ExitOnFailure --Dotted    misc/suites
    Stdout Should Be    dotted_exitonfailure.txt
    Stderr Should Be    empty.txt

--Dotted --ExitOnFailure with empty test case
    Run tests    -X.    core/empty_testcase_and_uk.robot
    Stdout Should Be    dotted_exitonfailure_empty_test.txt
    Stderr Should Be    empty.txt
    Check test tags    ${EMPTY}
    ${tc} =    Check test case    User Keyword Without Name    FAIL
    ...    Critical failure occurred and exit-on-failure mode is in use.
    Should contain    ${tc.tags}    robot:exit

*** Keywords ***
Run and verify tests
    [Arguments]    ${options}
    Run Tests    ${options}    misc/warnings_and_errors.robot
    Should Be Equal    ${SUITE.status}    PASS
    Length Should Be    ${SUITE.tests}    3

*** Settings ***
Force Tags        regression    pybot    jybot
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

--quiet
    Run and verify tests    --Quiet
    Stdout Should Be    empty.txt
    Stderr Should Be    warnings_and_errors_stderr.txt

Dotted does not show details for skipped
    Run tests    -.    running/fatal_exception
    Stdout Should Be    dotted_fatal_error.txt
    Stderr Should Be    empty.txt

*** Keywords ***
Run and verify tests
    [Arguments]    ${options}
    Run Tests    ${options}    misc/warnings_and_errors.robot
    Should Be Equal    ${SUITE.status}    PASS
    Length Should Be    ${SUITE.tests}    3

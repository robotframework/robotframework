*** Settings ***
Resource          console_resource.robot

*** Variables ***
${CONSOLES}       ${CURDIR}${/}..${/}..${/}..${/}testresources${/}consoles

*** Test Cases ***
Verbose
    Run and verify tests    --console verbose
    Stdout Should Be    warnings_and_errors_stdout.txt
    Stderr Should Be    warnings_and_errors_stderr.txt

Dotted
    Run and verify tests    --Console Dotted
    Stdout Should Be    warnings_and_errors_stdout_dotted.txt
    Stderr Should Be    warnings_and_errors_stderr.txt

Dotted with skip
    Run tests    --CONSOLE DOTTED --SKIPONFAILURE FAIL --NAME X    misc/pass_and_fail.robot misc/suites
    Stdout Should Be    dotted_with_skip.txt
    Stderr Should Be    empty.txt

Dotted with skip only
    Run tests    -. --skipon fail --skip pass    misc/pass_and_fail.robot
    Stdout Should Be    dotted_with_skip_only.txt
    Stderr Should Be    empty.txt

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

Custom console by path
    Run Tests    --console ${CONSOLES}${/}CustomConsole.py    misc/pass_and_fail.robot
    Stdout Should Contain    DEFAULT: Suite 'Pass And Fail' started
    Stdout Should Contain    DEFAULT: Test 'Pass' PASS
    Stdout Should Contain    DEFAULT: Test 'Fail' FAIL
    Stdout Should Contain    DEFAULT: Output:
    Stdout Should Contain    DEFAULT: Closing
    Stderr Should Be Empty

Custom console by path with argument
    Run Tests    --console ${CONSOLES}${/}CustomConsole.py:ARGUMENT    misc/pass_and_fail.robot
    Stdout Should Contain    ARGUMENT: Suite 'Pass And Fail' started
    Stdout Should Contain    ARGUMENT: Test 'Pass' PASS
    Stdout Should Contain    ARGUMENT: Closing
    Stderr Should Be Empty

Custom console by module name
    Run Tests    --console CustomConsole --pythonpath ${CONSOLES}    misc/pass_and_fail.robot
    Stdout Should Contain    DEFAULT: Suite 'Pass And Fail' started
    Stdout Should Contain    DEFAULT: Test 'Pass' PASS
    Stdout Should Contain    DEFAULT: Closing
    Stderr Should Be Empty

Custom console as module with functions
    Run Tests    --console ${CONSOLES}${/}module_console.py    misc/pass_and_fail.robot
    Stdout Should Contain    MODULE: Suite 'Pass And Fail' started
    Stdout Should Contain    MODULE: Test 'Pass' PASS
    Stdout Should Contain    MODULE: Closing
    Stdout Should Not Contain    Output:
    Stdout Should Not Contain    Report:
    Stdout Should Not Contain    Log:
    Stderr Should Be Empty

Custom console by dotted name
    Run Tests    --console CustomConsole.CustomConsole --pythonpath ${CONSOLES}    misc/pass_and_fail.robot
    Stdout Should Contain    DEFAULT: Suite 'Pass And Fail' started
    Stdout Should Contain    DEFAULT: Test 'Pass' PASS
    Stdout Should Contain    DEFAULT: Closing
    Stderr Should Be Empty

Custom console with named argument
    Run Tests    --console ${CONSOLES}${/}CustomConsole.py:name=NAMED    misc/pass_and_fail.robot
    Stdout Should Contain    NAMED: Suite 'Pass And Fail' started
    Stdout Should Contain    NAMED: Test 'Pass' PASS
    Stdout Should Contain    NAMED: Closing
    Stderr Should Be Empty

Custom console with wrong arguments
    Run Tests Without Processing Output    --console ${CONSOLES}${/}CustomConsole.py:too:many:args    misc/pass_and_fail.robot
    Stderr Should Start With    [ ERROR ] Taking console '

Non-existing custom console
    Run Tests Without Processing Output    --console NonExistent    misc/pass_and_fail.robot
    Stderr Should Start With    [ ERROR ] Taking console 'NonExistent' into use failed: Importing console 'NonExistent' failed: ModuleNotFoundError: No module named 'NonExistent'

--dotted
    Run and verify tests    --dotted
    Stdout Should Be    warnings_and_errors_stdout_dotted.txt
    Stderr Should Be    warnings_and_errors_stderr.txt

--dotted with --rpa
    Run and verify tests    --dotted --rpa
    Stdout Should Be    warnings_and_errors_stdout_dotted.txt    tests=tasks
    Stderr Should Be    warnings_and_errors_stderr.txt    tests=tasks

--quiet
    Run and verify tests    --Quiet
    Stdout Should Be    empty.txt
    Stderr Should Be    warnings_and_errors_stderr.txt

Dotted does not show details for skipped after fatal error
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
    Stderr Should Be    dotted_exitonfailure_empty_test_stderr.txt
    Check test tags    ${EMPTY}
    ${tc} =    Check test case    Empty Test Case    FAIL
    ...    Failure occurred and exit-on-failure mode is in use.
    Should contain    ${tc.tags}    robot:exit

*** Keywords ***
Run and verify tests
    [Arguments]    ${options}
    Run Tests    ${options}    misc/warnings_and_errors.robot
    Should Be Equal    ${SUITE.status}    PASS
    Length Should Be    ${SUITE.tests}    3

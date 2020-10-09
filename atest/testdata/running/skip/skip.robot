*** Settings ***
Library    skiplib.py

*** Variables ***
${TEST_OR_TASK}    Test

*** Test Cases ***
Skip Keyword
    [Documentation]    SKIP Skipped with Skip keyword.
    Skip
    Fail    Should not be executed!

Skip with Library Keyword
    [Documentation]    SKIP Show must not got on
    Skip with Message    Show must not got on
    Fail    Should not be executed!

Skip If Keyword with True Condition
    [Documentation]    SKIP 1 == 1
    Skip If    1 == 1

Skip If Keyword with True Condition And Custom Message
    [Documentation]    SKIP Skipped with abandon.
    Skip If    1 == 1    Skipped with abandon.

Skip If Keyword with False Condition
    [Documentation]    FAIL AssertionError
    Skip If    1 == 2
    Fail

Skip Keyword with Custom Message
    [Documentation]    SKIP Skipped due to reasons
    Skip    Skipped due to reasons
    Fail    Should not be executed!

Skipped in Setup 1
    [Documentation]    SKIP Setup skip
    [Setup]    Skip    Setup skip
    Fail    Should not be executed!

Skipped in Setup 2
    [Documentation]    SKIP Setup skip
    [Setup]    Run Keywords
    ...    No Operation    AND
    ...    Skip    Setup skip    AND
    ...    Fail    Should not be executed!
    Fail    Should not be executed!

Skipped with --skip
    [Tags]   skip-this
    [Documentation]    SKIP ${TEST_OR_TASK} skipped with --skip command line option.
    Fail

Skipped with --SkipOnFailure
    [Tags]   skip-on-failure
    [Documentation]    SKIP ${TEST_OR_TASK} skipped with --SkipOnFailure, original error:\nAssertionError
    Fail

--NonCritical Is an Alias for --SkipOnFailure
    [Tags]   non-crit
    [Documentation]    SKIP ${TEST_OR_TASK} skipped with --SkipOnFailure, original error:\nAssertionError
    Fail

--Critical can be used to override --SkipOnFailure
    [Tags]   dynamic-skip    crit
    [Documentation]    FAIL AssertionError
    Fail

Failing Test
    [Documentation]    FAIL AssertionError
    Fail

Passing Test
    No Operation

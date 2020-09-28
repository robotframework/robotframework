*** Settings ***
Library    skiplib.py

*** Test Cases ***
Skip Keyword
    [Documentation]    SKIP Skipped with Skip keyword.
    Skip

Skip with Library Keyword
    [Documentation]    SKIP Show must not got on
    Skip with Message    Show must not got on

Skip Keyword with Custom Message
    [Documentation]    SKIP Skipped due to reasons
    Skip    Skipped due to reasons

Skipped in Setup
    [Documentation]    SKIP Setup skip
    [Setup]    Skip     Setup skip
    Pass

Skipped with --skip
    [Tags]   skip-this
    [Documentation]    SKIP Test skipped with --skip command line option.
    Fail

Skipped with --SkipOnFailure
    [Tags]   skip-on-failure
    [Documentation]    SKIP Test skipped with --SkipOnFailure, original error:\nAssertionError
    Fail

--NonCritical Is an Alias for --SkipOnFailure
    [Tags]   non-crit
    [Documentation]    SKIP Test skipped with --SkipOnFailure, original error:\nAssertionError
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

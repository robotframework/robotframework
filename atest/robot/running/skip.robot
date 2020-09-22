*** Settings ***
Suite Setup     Run Tests  --SkipOnFailure dynamic-skip --noncritical non-crit --critical crit   running/skip/
Resource        atest_resource.robot

*** Test Cases ***
Skip Keyword
    Check Test Case     Skip Keyword

Skip with Library Keyword
    Check Test Case     Skip with Library Keyword

Skip Keyword with Custom Message
    Check Test Case     Skip Keyword with Custom Message

Skipped in Setup
    Check Test Case    Skipped in Setup

Skip in Suite Setup
    Check Test Case    Skipped due to Suite Setup    status=SKIP

Skip in Directory Suite Setup
    Check Test Case    Skip in Nested Suite

Skip with --SkipOnFailure
    Check Test Case    Skipped with --SkipOnFailure

Using Skip Does Not Affect Passing And Failing Tests
    Check Test Case    Passing Test
    Check Test Case    Failing Test

--NonCritical Is an Alias for --SkipOnFailure
    Check Test Case    --NonCritical Is an Alias for --SkipOnFailure

--Critical can be used to override --SkipOnFailure
    Check Test Case    --Critical can be used to override --SkipOnFailure

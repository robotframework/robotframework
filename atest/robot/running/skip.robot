*** Settings ***
Suite Setup     Run Tests  --skip skip-this --SkipOnFailure skip-on-failure --noncritical non-crit --critical crit   running/skip/
Resource        atest_resource.robot

*** Test Cases ***
Skip Keyword
    Check Test Case    ${TEST NAME}

Skip with Library Keyword
    Check Test Case    ${TEST NAME}

Skip Keyword with Custom Message
    Check Test Case    ${TEST NAME}

Skipped in Setup
    Check Test Case    ${TEST NAME} 1
    Check Test Case    ${TEST NAME} 2

Skip in Suite Setup
    Check Test Case    ${TEST NAME}

Skip in Directory Suite Setup
    Check Test Case    ${TEST NAME}

Skipped with --skip
    Check Test Case    ${TEST NAME}

Skipped with --SkipOnFailure
    Check Test Case    ${TEST NAME}

Using Skip Does Not Affect Passing And Failing Tests
    Check Test Case    Passing Test
    Check Test Case    Failing Test

--NonCritical Is an Alias for --SkipOnFailure
    Check Test Case    ${TEST NAME}

--Critical can be used to override --SkipOnFailure
    Check Test Case    ${TEST NAME}

*** Settings ***
Suite Setup     Run Tests  --skip skip-this --SkipOnFailure skip-on-failure --noncritical non-crit --critical crit   running/skip/
Resource        atest_resource.robot

*** Test Cases ***
Skip Keyword
    Check Test Case    ${TEST NAME}

Skip with Library Keyword
    Check Test Case    ${TEST NAME}

Skip with custom exception
    Check Test Case    ${TEST NAME}

Skip If Keyword with True Condition
    Check Test Case    ${TEST NAME}

Skip If Keyword with True Condition And Custom Message
    Check Test Case    ${TEST NAME}

Skip If Keyword with False Condition
    Check Test Case    ${TEST NAME}

Skip Keyword with Custom Message
    Check Test Case    ${TEST NAME}

Skip in Setup
    Check Test Case    ${TEST NAME}

Remaining setup keywords aren't run after skip
    Check Test Case    ${TEST NAME}

Skip in Teardown
    Check Test Case    ${TEST NAME}

Remaining teardown keywords aren't run after skip
    Check Test Case    ${TEST NAME}

Skip in Teardown After Failure In Body
    Check Test Case    ${TEST NAME}

Teardown is executed after skip
    ${tc} =    Check Test Case    ${TEST NAME}
    Check log message    ${tc.teardown.msgs[0]}    Teardown is executed!

Fail in Teardown After Skip In Body
    Check Test Case    ${TEST NAME}

Skip in Teardown After Skip In Body
    Check Test Case    ${TEST NAME}

Skip with Continuable Failure
    Check Test Case    ${TEST NAME}

Skip with Multiple Continuable Failures
    Check Test Case    ${TEST NAME}

Skip with Pass Execution in Teardown
    Check Test Case    ${TEST NAME}

Skip in Teardown with Pass Execution in Body
    Check Test Case    ${TEST NAME}

Skip in Teardown After Continuable Failures
    Check Test Case    ${TEST NAME}

Skip in Suite Setup
    Check Test Case    ${TEST NAME}

Skip in Directory Suite Setup
    Check Test Case    ${TEST NAME}

Skip In Suite Teardown
    Check Test Case    ${TEST NAME}

Skip In Directory Suite Teardown
    Check Test Case    ${TEST NAME}

Skip with Run Keyword and Ignore Error
    Check Test Case    ${TEST NAME}

Skip with Run Keyword and Expect Error
    Check Test Case    ${TEST NAME}

Skip with Run Keyword and Return Status
    Check Test Case    ${TEST NAME}

Skip with Wait Until Keyword Succeeds
    Check Test Case    ${TEST NAME}

Skipped with --skip
    Check Test Case    ${TEST NAME}

Skipped with --SkipOnFailure
    Check Test Case    ${TEST NAME}

Skipped with --SkipOnFailure when Failure in Test Setup
    Check Test Case    ${TEST NAME}

Skipped with --SkipOnFailure when Failure in Test Teardown
    Check Test Case    ${TEST NAME}

Skipped with --SkipOnFailure when Set Tags Used in Teardown
    Check Test Case    Skipped with --SkipOnFailure when Set Tags Used in Teardown

Using Skip Does Not Affect Passing And Failing Tests
    Check Test Case    Passing Test
    Check Test Case    Failing Test

--NonCritical Is an Alias for --SkipOnFailure
    Check Test Case    ${TEST NAME}

--Critical can be used to override --SkipOnFailure
    Check Test Case    ${TEST NAME}

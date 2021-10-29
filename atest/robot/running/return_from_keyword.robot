*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    running/return_from_keyword.robot
Resource         atest_resource.robot

*** Test Cases ***
Without return value
    Test And All Keywords Should Have Passed    allow not run=True

With single return value
    Test And All Keywords Should Have Passed    allow not run=True

With multiple return values
    Test And All Keywords Should Have Passed    allow not run=True

With variable
    Test And All Keywords Should Have Passed    allow not run=True

With list variable
    Test And All Keywords Should Have Passed    allow not run=True

Escaping
    Test And All Keywords Should Have Passed    allow not run=True

In nested keyword
    Test And All Keywords Should Have Passed    allow not run=True

Inside for loop in keyword
    Test And All Keywords Should Have Passed    allow not run=True

Keyword teardown is run
    Test And All Keywords Should Have Passed    allow not run=True

In a keyword inside keyword teardown
    Test And All Keywords Should Have Passed    allow not run=True

Fails if used directly in keyword teardown
    Check Test Case    ${TESTNAME}

Fails if used outside keywords
    Check Test Case    ${TESTNAME}

Fails if used outside keywords inside for loop
    Check Test Case    ${TESTNAME}

With continuable failure
    Check Test Case    ${TESTNAME}

With continuable failure in for loop
    Check Test Case    ${TESTNAME}

Return From Keyword If
    Test And All Keywords Should Have Passed        allow not run=True

Return From Keyword If does not evaluate bogus arguments if condition is untrue
    Check Test Case    ${TESTNAME}

Logs Info
    ${tc} =  Check Test Case    Without Return Value
    Check Log Message    ${tc.kws[0].kws[0].msgs[0]}
    ...    Returning from the enclosing user keyword.

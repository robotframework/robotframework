*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    standard_libraries/builtin/run_keywords.robot
Resource          atest_resource.robot

*** Test Cases ***
Passing keywords
    ${tc} =    Test Should Have Correct Keywords
    ...    BuiltIn.No Operation    Passing    BuiltIn.Log Variables
    Check Log Message    ${tc.kws[0].kws[1].kws[0].msgs[0]}    Hello, world!

Failing keyword
    Test Should Have Correct Keywords
    ...    Passing    Failing

Continuable failures
    Test Should Have Correct Keywords
    ...    Continuable failure    Multiple continuables    Failing

Keywords as variables
    Test Should Have Correct Keywords
    ...    BuiltIn.No Operation    Passing    BuiltIn.No Operation
    ...    Passing    BuiltIn.Log Variables    Failing

Non-existing variable as keyword name
    ${tc} =    Check Test Case    ${TESTNAME}
    Should Be Empty    ${tc.kws[0].kws}

Non-existing variable inside executed keyword
    Test Should Have Correct Keywords
    ...    Passing    Non-existing Variable

Non-existing keyword
    Test Should Have Correct Keywords
    ...    Passing    Non-Existing

Wrong number of arguments to keyword
    Test Should Have Correct Keywords
    ...    Passing    BuiltIn.Log

In test setup
    Check Test Case    ${TESTNAME}

In test teardown
    Check Test Case    ${TESTNAME}

In test teardown with ExecutionPassed exception
    Check Test Case    ${TESTNAME}

In test teardown with ExecutionPassed exception after continuable failure
    Check Test Case    ${TESTNAME}

In suite setup
    Check Log Message    ${SUITE.setup.kws[0].kws[0].msgs[0]}    Hello, world!
    Should Contain Keywords    ${SUITE.setup}    Passing    BuiltIn.No Operation

In suite teardown
    Should Contain Keywords    ${SUITE.teardown}    Failing    Passing    BuiltIn.Fail
    Should Be Equal    ${SUITE.message}    Suite teardown failed:\nSeveral failures occurred:\n\n1) Expected error message\n\n2) AssertionError

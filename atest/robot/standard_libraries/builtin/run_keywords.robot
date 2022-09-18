*** Settings ***
Documentation     Testing Run Keywords when used without AND. Tests with AND are in
...               run_keywords_with_arguments.robot.
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

Embedded arguments
    ${tc} =    Test Should Have Correct Keywords
    ...     Embedded "arg"    Embedded "\${1}"    Embedded object "\${OBJECT}"
    Check Log Message    ${tc.kws[0].kws[0].kws[0].msgs[0]}   arg
    Check Log Message    ${tc.kws[0].kws[1].kws[0].msgs[0]}   1
    Check Log Message    ${tc.kws[0].kws[2].kws[0].msgs[0]}   Robot

Embedded arguments with library keywords
    ${tc} =    Test Should Have Correct Keywords
    ...     embedded_args.Embedded "arg" in library
    ...     embedded_args.Embedded "\${1}" in library
    ...     embedded_args.Embedded object "\${OBJECT}" in library
    Check Log Message    ${tc.kws[0].kws[0].msgs[0]}   arg
    Check Log Message    ${tc.kws[0].kws[1].msgs[0]}   1
    Check Log Message    ${tc.kws[0].kws[2].msgs[0]}   Robot

Keywords names needing escaping
    Test Should Have Correct Keywords
    ...    Needs \\escaping \\\${notvar}

Continuable failures
    Test Should Have Correct Keywords
    ...    Continuable failure    Multiple continuables    Failing

Keywords as variables
    Test Should Have Correct Keywords
    ...    BuiltIn.No Operation    Passing    BuiltIn.No Operation
    ...    Passing    BuiltIn.Log Variables    Failing

Keywords names needing escaping as variable
    Test Should Have Correct Keywords
    ...    Needs \\escaping \\\${notvar}    Needs \\escaping \\\${notvar}
    ...    kw_index=1

Non-existing variable as keyword name
    Test Should Have Correct Keywords
    ...    Passing

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

In test teardown with non-existing variable in keyword name
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

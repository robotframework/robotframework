*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    variables/extended_variables.robot
Resource          atest_resource.robot

*** Test Cases ***
Using Attribute
    Check Test Case    ${TESTNAME}

Calling Method
    Check Test Case    ${TESTNAME}

Accessing List
    Check Test Case    ${TESTNAME}

Accessing Dictionary
    Check Test Case    ${TESTNAME}

Multiply
    Check Test Case    ${TESTNAME}

Failing When Base Name Does Not Exist
    Check Test Case    ${TESTNAME}

Failing When Base Name Starts With Existing Variable
    Check Test Case    ${TESTNAME} 1
    Check Test Case    ${TESTNAME} 2

Testing Extended Var Regexp
    Check Test Case    ${TESTNAME}

Base name contains non-ASCII characters
    Check Test Case    ${TESTNAME}

Escape characters and curly braces
    [Documentation]    This is somewhat complicated. See docs on test data side for details.
    Check Test Case    ${TESTNAME}

Failing When Attribute Does Not exists
    Check Test Case    ${TESTNAME} 1
    Check Test Case    ${TESTNAME} 2

Failing When Calling Method With Wrong Number Of Arguments
    Check Test Case    ${TESTNAME}

Failing When Method Raises Exception
    Check Test Case    ${TESTNAME}

Fail When Accessing Item Not In List
    Check Test Case    ${TESTNAME}

Fail When Accessing Item Not In Dictionary
    Check Test Case    ${TESTNAME}

Failing For Syntax Error
    Check Test Case    ${TESTNAME}

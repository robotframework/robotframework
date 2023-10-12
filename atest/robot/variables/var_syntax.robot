*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    variables/var_syntax.robot
Resource          atest_resource.robot

*** Test Cases ***
Scalar
    Check Test Case    ${TESTNAME}

Scalar with separator
    Check Test Case    ${TESTNAME}

List
    Check Test Case    ${TESTNAME}

Dict
    Check Test Case    ${TESTNAME}

Scopes
    Check Test Case    ${TESTNAME} 1
    Check Test Case    ${TESTNAME} 2

Invalid scope
    Check Test Case    ${TESTNAME}

Invalid scope from variable
    Check Test Case    ${TESTNAME}

Non-existing variable as scope
    Check Test Case    ${TESTNAME}

Non-existing variable in value
    Check Test Case    ${TESTNAME}

Non-existing variable in separator
    Check Test Case    ${TESTNAME}

With FOR
    Check Test Case    ${TESTNAME}

With WHILE
    Check Test Case    ${TESTNAME}

With IF
    Check Test Case    ${TESTNAME}

With inline IF
    Check Test Case    ${TESTNAME}

With TRY
    Check Test Case    ${TESTNAME}

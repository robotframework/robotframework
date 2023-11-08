*** Settings ***
Suite Setup     Run Tests  ${EMPTY}  standard_libraries/builtin/set_variable_if.robot
Resource        atest_resource.robot

*** Test Cases ***
True Condition
    Check Test Case  ${TESTNAME}

False Condition
    Check Test Case  ${TESTNAME}

Invalid Expression
    Check Test Case  ${TESTNAME}

Fails Without Values
    Check Test Case  ${TESTNAME} 1
    Check Test Case  ${TESTNAME} 2

Non-Existing Variables In Values
    Check Test Case  ${TESTNAME} 1
    Check Test Case  ${TESTNAME} 2
    Check Test Case  ${TESTNAME} 3
    Check Test Case  ${TESTNAME} 4
    Check Test Case  ${TESTNAME} 5

Extra Values Are Ignored If First Expression Is True
    Check Test Case  ${TESTNAME}

If / Else If
    Check Test Case  ${TESTNAME}

If / Else If / Else
    Check Test Case  ${TESTNAME}

With Empty List Variables
    Check Test Case  ${TESTNAME} 1
    Check Test Case  ${TESTNAME} 2
    Check Test Case  ${TESTNAME} 3

With List Variables In Values
    Check Test Case  ${TESTNAME}

With List Variables In Expressions And Values
    Check Test Case  ${TESTNAME}

With List Variables Containing Escaped Values
    Check Test Case  ${TESTNAME}

Lot of conditions
    Check Test Case  ${TESTNAME}

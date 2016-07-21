*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    standard_libraries/builtin/evaluate.robot
Resource         atest_resource.robot

*** Test Cases ***
Evaluate
    Check Test Case    ${TESTNAME}

Evaluate With Modules
    Check Test Case    ${TESTNAME}

Evaluate With Namespace
    Check Test Case    ${TESTNAME}

Evaluate with Get Variables Namespace
    Check Test Case    ${TESTNAME}

Evaluate with Non-dict Namespace
    Check Test Case    ${TESTNAME}

Evaluate gets variables automatically
    Check Test Case    ${TESTNAME}

Automatic variables don't work in strings
    Check Test Case    ${TESTNAME}

Automatic variables don't override Python built-ins
    Check Test Case    ${TESTNAME}

Automatic variables don't override custom namespace
    Check Test Case    ${TESTNAME}

Automatic variables don't override modules
    Check Test Case    ${TESTNAME}

Automatic variables are case and underscore insensitive
    Check Test Case    ${TESTNAME}

Automatic variable from variable
    Check Test Case    ${TESTNAME}

Non-existing automatic variable
    Check Test Case    ${TESTNAME}

Non-existing automatic variable with recommendation
    Check Test Case    ${TESTNAME} 1
    Check Test Case    ${TESTNAME} 2

Invalid $ usage
    Check Test Case    ${TESTNAME} 1
    Check Test Case    ${TESTNAME} 2
    Check Test Case    ${TESTNAME} 3
    Check Test Case    ${TESTNAME} 4
    Check Test Case    ${TESTNAME} 5
    Check Test Case    ${TESTNAME} 6
    Check Test Case    ${TESTNAME} 7
    Check Test Case    ${TESTNAME} 8

Evaluate Empty
    Check Test Case    ${TESTNAME}

Evaluate Nonstring
    Check Test Case    ${TESTNAME}

Evaluate doesn't see module globals
    Check Test Case    ${TESTNAME}

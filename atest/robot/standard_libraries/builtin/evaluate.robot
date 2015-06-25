*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    standard_libraries/builtin/evaluate.robot
Force Tags       regression    pybot    jybot
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

Evaluate gets Variables automatically
    Check Test Case    ${TESTNAME}

Variables don't override python builtins
    Check Test Case    ${TESTNAME}

Variables don't override custom namespace
    Check Test Case    ${TESTNAME}

Variables don't override modules
    Check Test Case    ${TESTNAME}

Variables are case and underscore insensitive
    Check Test Case    ${TESTNAME}

Evaluate Empty
    Check Test Case    ${TESTNAME}

Evaluate Nonstring
    Check Test Case    ${TESTNAME}

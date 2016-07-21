*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    keywords/named_args/with_user_keywords.robot
Resource          atest_resource.robot

*** Test Cases ***
Simple Kwarg
    Check Test Case    ${TESTNAME}

Kwarg Syntax In Variable Is Ignored
    Check Test Case    ${TESTNAME}

Non-string value in UK kwarg
    Check Test Case    ${TESTNAME}

Equals Sign In Kwarg Value
    Check Test Case    ${TESTNAME}

Using non-existing kwarg
    Check Test Case    ${TESTNAME}

Escaping Kwarg
    Check Test Case    ${TESTNAME}

Mandatory Args Should Be Positioned
    Check Test Case    ${TESTNAME}

Inside Run Kw
    Check Test Case    ${TESTNAME}

Default value with escaped content
    Check Test Case    ${TESTNAME}

Varargs without naming arguments works
    Check Test Case    ${TESTNAME}

Naming without the varargs works
    Check Test Case    ${TESTNAME}

Varargs with naming does not work
    Check Test Case    ${TESTNAME}

Varargs with naming does not work with empty lists either
    Check Test Case    ${TESTNAME}

Named combinations with varargs
    Check Test Case    ${TESTNAME}

Non working named combinations with varargs
    Check Test Case    ${TESTNAME}

Named combinations without varargs
    Check Test Case    ${TESTNAME}

Non working named combinations without varargs
    Check Test Case    ${TESTNAME}

Nön äscii named arguments
    Check Test Case    ${TESTNAME}

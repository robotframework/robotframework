*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    keywords/named_args/with_python_keywords.robot
Resource         atest_resource.robot

*** Test Cases ***
Simple Named
    Check Test Case    ${TESTNAME}

Mandatory And Named As Positional
    Check Test Case    ${TESTNAME}

Mandatory And Named As Named
    Check Test Case    ${TESTNAME}

Same Argument As Positional And Named Fails
    Check Test Case    ${TESTNAME}

Mandatory, Named And Varargs As Positional
    Check Test Case    ${TESTNAME}

Naming arguments with varargs is supported when varargs are not used
    Check Test Case    ${TESTNAME}

Naming arguments is not supported when varargs are used
    Check Test Case    ${TESTNAME}

Naming arguments before possible varargs is not supported with empty lists either
    Check Test Case    ${TESTNAME}

Named Syntax In Variable Is Ignored
    Check Test Case    ${TESTNAME}

Non-string named value
    Check Test Case    ${TESTNAME}

Equals Sign In Named Value
    Check Test Case    ${TESTNAME}

Non-existing argument does not trigger named usage
    Check Test Case    ${TESTNAME}

Run Keyword's own named arguments are not resolved
    Check Test Case    ${TESTNAME}

Inside Run Keyword named arguments are resolved
    Check Test Case    ${TESTNAME}

Named combinations with varargs
    Check Test Case    ${TESTNAME}

Kwargs alone
    Check Test Case    ${TESTNAME}

Kwargs with escaped equal sign
    Check Test Case    ${TESTNAME} 1
    Check Test Case    ${TESTNAME} 2

Kwargs with positional and named
    Check Test Case    ${TESTNAME}

Non working named combinations with varargs
    Check Test Case    ${TESTNAME}

Non working combinations with kwargs
    Check Test Case    ${TESTNAME}

Named combinations without varargs
    Check Test Case    ${TESTNAME}

Non working named combinations without varargs
    Check Test Case    ${TESTNAME}

Working combinations with all argument types
    Check Test Case    ${TESTNAME}

Test escaping with all argument types
    Check Test Case    ${TESTNAME}

Illegal combinations with all argument types
    Check Test Case    ${TESTNAME}

Multiple named with same name is allowed and last has precedence
    Check Test Case    ${TESTNAME}

List variable with multiple values for same variable
    Check Test Case    ${TESTNAME}

Nön äscii allowed in keyword argument names
    Check Test Case    ${TESTNAME}

Empty string is allowed in kwargs names
    Check Test Case    ${TESTNAME}

Dict is not converted to kwargs
    Check Test Case    ${TESTNAME}

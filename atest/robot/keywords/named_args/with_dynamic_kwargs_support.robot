*** Settings ***
Documentation     Tests dynamic library that accepts **kwargs.
...               Most tests are same as in with_dynamic_keywords.robot
...               but there are tests at the end that actually use **kwargs.
Suite Setup       Run Tests
...    --variable DynamicLibrary:DynamicLibraryWithKwargsSupport
...    keywords/named_args/with_dynamic_keywords.robot keywords/named_args/with_dynamic_kwargs_support.robot
Resource          atest_resource.robot

*** Test Cases ***
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

Named arguments are set defaults only when needed
    Check Test Case    ${TESTNAME}

Non working named combinations without varargs
    Check Test Case    ${TESTNAME}

Nön äscii named arguments
    Check Test Case    ${TESTNAME}

# Tests above same as in with_dynamic_keywords.robot but the library is different.
# Test below actually use **kwargs.

Named combinations with kwargs
    Check Test Case    ${TESTNAME}

Non working named combinations with kwargs
    Check Test Case    ${TESTNAME}

Named combinations with varargs and kwargs
    Check Test Case    ${TESTNAME}

Non working named combinations with varargs and kwargs
    Check Test Case    ${TESTNAME}

Multiple named with same name is allowed and last has precedence
    Check Test Case    ${TESTNAME} 1
    Check Test Case    ${TESTNAME} 2

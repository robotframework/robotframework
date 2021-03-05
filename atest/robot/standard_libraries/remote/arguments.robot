*** Settings ***
Suite Setup      Run Remote Tests    arguments.robot    arguments.py
Resource         remote_resource.robot

*** Test Cases ***
No Arguments
    Check Test Case    ${TESTNAME}

Required Arguments
    Check Test Case    ${TESTNAME}

Arguments With Default Values
    Check Test Case    ${TESTNAME}

Defaults as tuples
    Check Test Case    ${TESTNAME}

Arguent conversion based on defaults
    Check Test Case    ${TESTNAME}

Named Arguments
    Check Test Case    ${TESTNAME}

Variable Number Of Arguments
    Check Test Case    ${TESTNAME}

Required Arguments, Default Values and Varargs
    Check Test Case    ${TESTNAME}

No kwargs
    Check Test Case    ${TESTNAME}

One kwarg
    Check Test Case    ${TESTNAME}

Multiple kwargs
    Check Test Case    ${TESTNAME}

Keyword-only args
    Check Test Case    ${TESTNAME}

Keyword-only args with default
    Check Test Case    ${TESTNAME}

Args and kwargs
    Check Test Case    ${TESTNAME}

Varargs and kwargs
    Check Test Case    ${TESTNAME}

All arg types
    Check Test Case    ${TESTNAME}

Using Arguments When No Accepted
    Check Test Case    ${TESTNAME}

Using Positional Arguments When Only Kwargs Accepted
    Check Test Case    ${TESTNAME}

Too Few Arguments When Using Only Required Args
    Check Test Case    ${TESTNAME}

Too Many Arguments When Using Only Required Args
    Check Test Case    ${TESTNAME}

Too Few Arguments When Using Default Values
    Check Test Case    ${TESTNAME}

Too Many Arguments When Using Default Values
    Check Test Case    ${TESTNAME}

Too Few Arguments When Using Varargs
    Check Test Case    ${TESTNAME}

Named arguments before positional
    Check Test Case    ${TESTNAME}

Argument types as list
    Check Test Case    ${TESTNAME}

Argument types as dict
    Check Test Case    ${TESTNAME}

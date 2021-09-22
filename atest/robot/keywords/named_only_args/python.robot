*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    keywords/named_only_args/python.robot
Resource         atest_resource.robot

*** Test Cases ***
Mandatory arguments
    Check Test Case    ${TESTNAME}

Default values
    Check Test Case    ${TESTNAME}

Mandatory Can Be After Default
    Check Test Case    ${TESTNAME}

Annotation
    Check Test Case    ${TESTNAME}

Annotation and default value
    Check Test Case    ${TESTNAME}

Last given value has precedence
    Check Test Case    ${TESTNAME}

Missing value
    Check Test Case    ${TESTNAME}

Missing multiple values
    Check Test Case    ${TESTNAME}

Unexpected keyword argument
    Check Test Case    ${TESTNAME}

Multiple unexpected keyword argument
    Check Test Case    ${TESTNAME}

Unexpected positional argument
    Check Test Case    ${TESTNAME} 1
    Check Test Case    ${TESTNAME} 2

With varargs
    Check Test Case    ${TESTNAME}

With other arguments
    Check Test Case    ${TESTNAME}

Argument name as variable
    Check Test Case    ${TESTNAME}

Argument name as non-existing variable
    Check Test Case    ${TESTNAME}

With positional argument containing equal sign
    Check Test Case    ${TESTNAME}

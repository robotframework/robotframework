*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    keywords/named_only_args/user_keyword.robot
Resource         atest_resource.robot

*** Test Cases ***
Mandatory arguments
    Check Test Case    ${TESTNAME}

Default values
    Check Test Case    ${TESTNAME}

Mandatory Can Be After Default
    Check Test Case    ${TESTNAME}

Variable in default value
    Check Test Case    ${TESTNAME}

Last given value has precedence
    Check Test Case    ${TESTNAME}

Missing value
    Check Test Case    ${TESTNAME} 1
    Check Test Case    ${TESTNAME} 2

Missing multiple values
    Check Test Case    ${TESTNAME}

Unexpected keyword argumemt
    Check Test Case    ${TESTNAME}

Multiple unexpected keyword argumemt
    Check Test Case    ${TESTNAME}

Unexpected positional argument
    Check Test Case    ${TESTNAME} 1
    Check Test Case    ${TESTNAME} 2

With varargs
    Check Test Case    ${TESTNAME}

With other arguments
    Check Test Case    ${TESTNAME}

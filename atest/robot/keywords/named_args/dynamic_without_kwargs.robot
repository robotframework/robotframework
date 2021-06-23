*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    keywords/named_args/dynamic_without_kwargs.robot
Resource         atest_resource.robot

*** Test Cases ***
Simple usage
    Check Test Case    ${TESTNAME}

Variable in name
    Check Test Case    ${TESTNAME}

Order does not matter
    Check Test Case    ${TESTNAME}

Last named wins
    Check Test Case    ${TESTNAME}

Positional and named
    Check Test Case    ${TESTNAME}

Values with defaults can be omitted at the end
    Check Test Case    ${TESTNAME}

Values with defaults can be omitted in the middle
    [Documentation]    Default values are used to fill the gaps.
    Check Test Case    ${TESTNAME}

Non-string values
    Check Test Case    ${TESTNAME}

Nön-ÄSCII values
    Check Test Case    ${TESTNAME}

Nön-ÄSCII names
    Check Test Case    ${TESTNAME}

Equal sign in value
    Check Test Case    ${TESTNAME}

Equal sign from variable
    Check Test Case    ${TESTNAME}

Equal sign with non-existing name
    Check Test Case    ${TESTNAME}

Escaping equal sign
    Check Test Case    ${TESTNAME}

Escaping value
    Check Test Case    ${TESTNAME}

Inside "Run Keyword"
    Check Test Case    ${TESTNAME}

Varargs without naming works
    Check Test Case    ${TESTNAME}

Naming without varargs works
    Check Test Case    ${TESTNAME}

Positional after named
    Check Test Case    ${TESTNAME} 1
    Check Test Case    ${TESTNAME} 2
    Check Test Case    ${TESTNAME} 3

Missing argument
    Check Test Case    ${TESTNAME}

Both positional and named value
    Check Test Case    ${TESTNAME} 1
    Check Test Case    ${TESTNAME} 2

*** Settings ***
Documentation     Handling valid and invalid arguments with Python keywords.
Suite Setup       Run Tests    ${EMPTY}    keywords/python_arguments.robot
Resource          atest_resource.robot

*** Test Cases ***
Correct Number Of Arguments When No Defaults Or Varargs
    Check Test Case    ${TESTNAME}

Too Few Arguments When No Defaults Or Varargs
    Check Test Case    ${TESTNAME} 1
    Check Test Case    ${TESTNAME} 2

Too Many Arguments When No Defaults Or Varargs
    Check Test Case    ${TESTNAME} 1
    Check Test Case    ${TESTNAME} 2
    Check Test Case    ${TESTNAME} 3

Correct Number Of Arguments With Defaults
    Check Test Case    ${TESTNAME}

Too Few Arguments With Defaults
    Check Test Case    ${TESTNAME}

Too Many Arguments With Defaults
    Check Test Case    ${TESTNAME} 1
    Check Test Case    ${TESTNAME} 2

Correct Number Of Arguments With Varargs
    Check Test Case    ${TESTNAME}

Too Few Arguments With Varargs
    Check Test Case    ${TESTNAME}

Correct Number Of Arguments With Defaults And Varargs
    Check Test Case    ${TESTNAME}

Too Few Arguments With Defaults And Varargs
    Check Test Case    ${TESTNAME}

Calling Using List Variables
    Check Test Case    ${TESTNAME}

Calling Using Annotations
    Check Test Case    ${TESTNAME}

Calling Using Annotations With Defaults
    Check Test Case    ${TESTNAME}

Dummy decorator does not preserve arguments
    Check Test Case    ${TESTNAME} 1
    Check Test Case    ${TESTNAME} 2

Decorator using functools.wraps preserves arguments
    Check Test Case    ${TESTNAME}

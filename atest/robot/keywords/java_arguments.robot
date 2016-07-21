*** Settings ***
Documentation     Handling valid and invalid arguments with Java keywords.
...               Related tests also in test_libraries/java_libraries.robot.
Suite Setup       Run Tests    ${EMPTY}    keywords/java_arguments.robot
Force Tags        require-jython
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

Java Varargs Should Work
    Check Test Case    ${TESTNAME}

Too Few Arguments With Varargs
    Check Test Case    ${TESTNAME}

Too Few Arguments With Varargs List
    Check Test Case    ${TESTNAME}

Varargs Work Also With Arrays
    [Documentation]    Make sure varargs support doesn't make it impossible to used Java arrays and Python lists with Java keyword expecting arrays.
    Check Test Case    ${TESTNAME}

Varargs Work Also With Lists
    [Documentation]    Make sure varargs support doesn't make it impossible to used Java arrays and Python lists with Java keyword expecting arrays.
    Check Test Case    ${TESTNAME}

Kwargs
    Check Test Case    ${TESTNAME}

Normal and Kwargs
    Check Test Case    ${TESTNAME}

Varargs and Kwargs
    Check Test Case    ${TESTNAME}

All args
    Check Test Case    ${TESTNAME}

Too many positional with kwargs
    Check Test Case    ${TESTNAME} 1
    Check Test Case    ${TESTNAME} 2

Java kwargs wont be interpreted as values for positional arguments
    Check Test Case    ${TESTNAME}

Map can be given as an argument still
    Check Test Case    ${TESTNAME}

Dict can be given as an argument still
    Check Test Case    ${TESTNAME}

Hashmap is not kwargs
    Check Test Case    ${TESTNAME}

Valid Arguments For Keyword Expecting Non String Scalar Arguments
    Check Test Case    ${TESTNAME}

Valid Arguments For Keyword Expecting Non String Array Arguments
    Check Test Case    ${TESTNAME}

Valid Arguments For Keyword Expecting Non String List Arguments
    Check Test Case    ${TESTNAME}

Invalid Argument Types
    Check Test Case    ${TESTNAME} 1
    Check Test Case    ${TESTNAME} 2
    Check Test Case    ${TESTNAME} 3
    Check Test Case    ${TESTNAME} 4
    Check Test Case    ${TESTNAME} 5
    Check Test Case    ${TESTNAME} 6
    Check Test Case    ${TESTNAME} 7

Calling Using List Variables
    Check Test Case    ${TESTNAME}

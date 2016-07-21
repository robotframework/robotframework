*** Settings ***
Suite Setup      Run Tests    --dryrun    keywords/java_arguments.robot
Force Tags       require-jython
Resource         atest_resource.robot

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

Java Varargs Should Work
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

Too Few Arguments With Varargs List
    Check Test Case    ${TESTNAME}

Varargs Work Also With Arrays
    Check Test Case    ${TESTNAME}

Varargs Work Also With Lists
    Check Test Case    ${TESTNAME}

Invalid Argument Types
    Check Test Case    ${TESTNAME} 1

Invalid Argument Values Are Not Checked
    Check Test Case    Invalid Argument Types 3    PASS    ${EMPTY}

Arguments with variables are not coerced
    Check Test Case    Invalid Argument Types 2    PASS    ${EMPTY}
    Check Test Case    Invalid Argument Types 3    PASS    ${EMPTY}
    Check Test Case    Invalid Argument Types 4    PASS    ${EMPTY}
    Check Test Case    Invalid Argument Types 5    PASS    ${EMPTY}
    Check Test Case    Invalid Argument Types 6    PASS    ${EMPTY}
    Check Test Case    Invalid Argument Types 7    PASS    ${EMPTY}

Calling Using List Variables
    Check Test Case    ${TESTNAME}

*** Settings ***
Documentation     Handling valid and invalid user keyword arguments.
Suite Setup       Run Tests    ${EMPTY}    keywords/user_keyword_arguments.robot
Force Tags        regression    pybot    jybot
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

Default With Variable
    Check Test Case    ${TESTNAME}

Local Variable Does Not Affect Variable In Default Value
    Check Test Case    ${TESTNAME}

Explicitly Set Variable Affects Variable In Default Value
    Check Test Case    ${TESTNAME}

Default With Automatic Variable
    Check Test Case    ${TESTNAME}

Default With Extended Variable Syntax
    Check Test Case    ${TESTNAME}

Calling Using List Variables
    Check Test Case    ${TESTNAME}

Calling Using Dict Variables
    Check Test Case    ${TESTNAME}

Caller does not see modifications to varargs
    Check Test Case    ${TESTNAME}

Invalid Arguments Spec
    [Template]    Verify Invalid Argument Spec
    0    Invalid argument syntax    Invalid argument syntax 'no deco'.
    1    Non-default after defaults    Non-default argument after default arguments.
    2    Varargs not last    Positional argument after varargs.

*** Keywords ***
Verify Invalid Argument Spec
    [Arguments]    ${index}    ${name}    ${error}
    Check Test Case    ${TEST NAME} - ${name}
    Check Log Message    ${ERRORS[${index}]}
    ...    Creating user keyword '${name}' failed: Invalid argument specification: ${error}    ERROR

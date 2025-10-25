*** Settings ***
Documentation     Handling valid and invalid user keyword arguments.
Suite Setup       Run Tests    ${EMPTY}    keywords/user_keyword_arguments.robot
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

Default With Non-Existing Variable
    Check Test Case    ${TESTNAME}

Local Variable Does Not Affect Variable In Default Value
    Check Test Case    ${TESTNAME}

Explicitly Set Variable Affects Variable In Default Value
    Check Test Case    ${TESTNAME}

Default With Automatic Variable
    Check Test Case    ${TESTNAME}

Default With Extended Variable Syntax
    Check Test Case    ${TESTNAME}

Default With Variable Based On Earlier Argument
    Check Test Case    ${TESTNAME}

Default With List Variable
    Check Test Case    ${TESTNAME}

Default With Invalid List Variable
    Check Test Case    ${TESTNAME}

Default With Dict Variable
    Check Test Case    ${TESTNAME}

Default With Invalid Dict Variable
    Check Test Case    ${TESTNAME}

Argument With `=` In Name
    Check Test Case    ${TESTNAME}

Calling Using List Variables
    Check Test Case    ${TESTNAME}

Calling Using Dict Variables
    Check Test Case    ${TESTNAME}

Caller does not see modifications to varargs
    Check Test Case    ${TESTNAME}

Invalid Arguments Spec
    [Template]    Verify Invalid Argument Spec
    0    Invalid argument syntax               Invalid argument syntax 'no deco'.
    1    Non-default after default             Non-default argument after default arguments.
    2    Non-default after default w/ types    Non-default argument after default arguments.
    3    Default with varargs                  Only normal arguments accept default values, list arguments like '\@{varargs}' do not.
    4    Default with kwargs                   Only normal arguments accept default values, dictionary arguments like '\&{kwargs}' do not.
    5    Multiple varargs                      Cannot have multiple varargs.
    6    Multiple varargs w/ types             Cannot have multiple varargs.
    7    Kwargs not last                       Only last argument can be kwargs.
    8    Kwargs not last w/ types              Only last argument can be kwargs.
    9    Multiple errors                       Multiple errors:
    ...                                        - Invalid argument syntax 'invalid'.
    ...                                        - Non-default argument after default arguments.
    ...                                        - Cannot have multiple varargs.
    ...                                        - Only last argument can be kwargs.

*** Keywords ***
Verify Invalid Argument Spec
    [Arguments]    ${index}    ${name}    @{error}
    Check Test Case    ${TEST NAME} - ${name}
    VAR    ${error}     @{error}    separator=\n
    VAR    ${lineno}    ${{358 + ${index} * 4}}
    Error In File    ${index}    keywords/user_keyword_arguments.robot    ${lineno}
    ...    Creating keyword '${name}' failed:
    ...    Invalid argument specification: ${error}

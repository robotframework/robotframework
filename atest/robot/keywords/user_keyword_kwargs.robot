*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    keywords/user_keyword_kwargs.robot
Resource         atest_resource.robot

*** Test Cases ***
Kwargs only
    Check Test Case    ${TESTNAME}

Positional and kwargs
    Check Test Case    ${TESTNAME}

Positional with defaults and kwargs
    Check Test Case    ${TESTNAME}

Varags and kwargs
    Check Test Case    ${TESTNAME}

Positional, varargs and kwargs
    Check Test Case    ${TESTNAME}

Positional with defaults, varargs and kwargs
    Check Test Case    ${TESTNAME}

Kwargs are ordered
    Check Test Case    ${TESTNAME}

Kwargs are dot-accessible
    Check Test Case    ${TESTNAME}

Too few positional arguments
    Check Test Case    ${TESTNAME}

Too many positional arguments
    Check Test Case    ${TESTNAME}

Positional after kwargs
    Check Test Case    ${TESTNAME}

Non-String Keys
    Check Test Case    ${TESTNAME}

Calling using dict variables
    Check Test Case    ${TESTNAME}

Caller does not see modifications to kwargs
    Check Test Case    ${TESTNAME}

Invalid arguments spec
    [Template]    Verify Invalid Argument Spec
    0    182    Positional after kwargs    Only last argument can be kwargs.
    1    186    Varargs after kwargs       Only last argument can be kwargs.

*** Keywords ***
Verify Invalid Argument Spec
    [Arguments]    ${index}    ${lineno}    ${name}    ${error}
    Check Test Case    ${TEST NAME}: ${name}
    Error In File    ${index}    keywords/user_keyword_kwargs.robot    ${lineno}
    ...    Creating keyword '${name}' failed:
    ...    Invalid argument specification: ${error}

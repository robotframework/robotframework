*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    keywords/type_conversion/type_statement.robot
Test Tags         require-py3.12
Resource          atest_resource.robot

*** Test Cases ***
Simple value
    Check Test Case    ${TESTNAME}

Params in value
    Check Test Case    ${TESTNAME}

Union value
    Check Test Case    ${TESTNAME}

Forward reference
    Check Test Case    ${TESTNAME}

Recursion
    Check Test Case    ${TESTNAME}

Failing recursive conversion
    Check Test Case    ${TESTNAME}

Generic simple
    Check Test Case    ${TESTNAME}

Generic with params in value
    Check Test Case    ${TESTNAME}

Generic with union
    Check Test Case    ${TESTNAME}

Generic with defaults
    [Tags]    require-py3.13
    Check Test Case    ${TESTNAME}

Generic forward reference
    Check Test Case    ${TESTNAME}

Invalid
    VAR    ${message}
    ...    Error in library 'TypeStatement':
    ...    Adding keyword 'invalid' failed:
    ...    Resolving type alias 'Invalid' failed:
    ...    name 'NonExisting' is not defined
    Check Log Message    ${ERRORS}[-1]    ${message}    ERROR

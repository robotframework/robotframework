*** Settings ***
Suite Setup       Run Keywords
...               Remove Environment Variable    PYTHONCASEOK    AND
...               Run Tests    ${EMPTY}    variables/python_evaluation.robot
Suite Teardown    Set Environment Variable    PYTHONCASEOK    True
Resource          atest_resource.robot

*** Test Cases ***
Python only
    Check Test Case    ${TESTNAME}

Variable replacement
    Check Test Case    ${TESTNAME}

Inline variables
    Check Test Case    ${TESTNAME}

Automatic module import
    Check Test Case    ${TESTNAME}

Module imports are case-sensitive
    Check Test Case    ${TESTNAME}

Nested usage
    Check Test Case    ${TESTNAME}

Variable section
    Check Test Case    ${TESTNAME}

Escape characters and curly braces
    Check Test Case    ${TESTNAME}

Invalid
    Check Test Case    ${TESTNAME}

Invalid in variable table
    [Template]    Validate invalid variable error
    4      \${NON EXISTING MODULE}
    ...    Resolving variable '\${{i_do_not_exist}}' failed:
    ...    Evaluating expression 'i_do_not_exist' failed:
    ...    NameError: name 'i_do_not_exist' is not defined nor importable as module
    5      \${NON EXISTING VARIABLE}
    ...    Resolving variable '\${{$i_do_not_exist}}' failed:
    ...    Evaluating expression '$i_do_not_exist' failed:
    ...    Variable '$i_do_not_exist' not found.
    2      \${INVALID EXPRESSION}
    ...    Resolving variable '\${{ 1/0 }}' failed:
    ...    Evaluating expression '1/0' failed:
    ...    ZeroDivisionError: *
    ...    pattern=True
    3      \${INVALID SYNTAX}
    ...    Variable '\${{ 1/1 }' was not closed properly.
    6      \${RECURSION}
    ...    Recursive variable definition.
    1      \${RECURSION INDIRECT}
    ...    Resolving variable '\${{ $INDIRECT_RECURSION }}' failed:
    ...    Evaluating expression '$INDIRECT_RECURSION' failed:
    ...    Variable '\${INDIRECT_RECURSION}' not found.
    0      \${INDIRECT RECURSION}
    ...    Recursive variable definition.

*** Keywords ***
Validate invalid variable error
    [Arguments]    ${index}    ${name}    @{error}    ${pattern}=False
    ${path} =    Normalize path    ${DATADIR}/variables/python_evaluation.robot
    ${error} =    Catenate    @{error}
    ${message} =    Catenate
    ...    Error in file '${path}': Setting variable '${name}' failed: ${error}
    Check log message    ${ERRORS}[${index}]    ${message}    ERROR    pattern=${pattern}

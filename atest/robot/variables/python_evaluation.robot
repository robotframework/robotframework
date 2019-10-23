*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    variables/python_evaluation.robot
Resource         atest_resource.robot

*** Test Cases ***
Python only
    Check Test Case    ${TESTNAME}

Variable replacement
    Check Test Case    ${TESTNAME}

Inline variables
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
    4      \${NON EXISTING}
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
    5      \${RECURSION}
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

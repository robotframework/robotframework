*** Settings ***
Suite Setup       Run Tests With Environment Variables
Resource          atest_resource.robot

*** Test Cases ***
Get Environment Variable
    Check test case    ${TEST NAME}

Set Environment Variable
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc[0, 0]}    Arguments: [ 'EXAMPLE_ENV_VAR_32FDHT' | 'Hello' ]    level=TRACE
    Check Log Message    ${tc[0, 1]}    Environment variable 'EXAMPLE_ENV_VAR_32FDHT' set to value 'Hello'.

Set Environment Variable with Secret Content
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc[0, 0]}    Arguments: [ 'EXAMPLE_ENV_VAR_32FDHT' | Secret(value=<secret>) ]    level=TRACE
    Check Log Message    ${tc[0, 1]}    Environment variable 'EXAMPLE_ENV_VAR_32FDHT' set to a secret value.

Append To Environment Variable
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc[0, 0]}    Arguments: [ 'EXAMPLE_ENV_VAR_32FDHT' | 'first' ]    level=TRACE
    Check Log Message    ${tc[0, 1]}    Environment variable 'EXAMPLE_ENV_VAR_32FDHT' set to value 'first'.

Append To Environment Variable With Custom Separator
    Check test case    ${TEST NAME}

Append To Environment Variable With Invalid Config
    Check test case    ${TEST NAME}

Append To Environment Variable With Secret Value
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc[0, 0]}    Arguments: [ 'EXAMPLE_ENV_VAR_32FDHT' | Secret(value=<secret>) ]    level=TRACE
    Check Log Message    ${tc[0, 1]}    Environment variable 'EXAMPLE_ENV_VAR_32FDHT' set to a secret value.
    Check Log Message    ${tc[2, 0]}    Arguments: [ 'EXAMPLE_ENV_VAR_32FDHT' | 'This is not!' | Secret(value=<secret>) | separator=' ' ]    level=TRACE
    Check Log Message    ${tc[2, 1]}    Environment variable 'EXAMPLE_ENV_VAR_32FDHT' set to a secret value.

Remove Environment Variable
    Check test case    ${TEST NAME}

Remove Multiple Environment Variables
    Check test case    ${TEST NAME}

Environment Variable Should Be Set
    Check test case    ${TEST NAME}

Environment Variable Should Be Set With Non Default Error
    Check test case    ${TEST NAME}

Environment Variable Should Not Be Set
    Check test case    ${TEST NAME}

Environment Variable Should Not Be Set With Non Default Error
    Check test case    ${TEST NAME}

Set Environment Variable In One Test And Use In Another
    Check test case    ${TEST NAME}, Part 1
    Check test case    ${TEST NAME}, Part 2

Get And Log Environment Variables
    ${tc}=    Check test case    ${TEST NAME}
    Check log message    ${tc[9, 1]}    0 = value
    Check log message    ${tc[9, 2]}    1 = äiti

Non-string names and values are converted to strings automatically
    Check test case    ${TEST NAME}

Non-ASCII names and values are encoded automatically
    Check test case    ${TEST NAME}

Non-ASCII variable set before execution
    Check test case    ${TEST NAME}

Use NON-ASCII variable in child process
    Check test case    ${TEST NAME}

*** Keywords ***
Run Tests With Environment Variables
    Set Environment Variable    NON_ASCII_BY_RUNNER    I can häs åäö?!??!¿¿¡¡
    Run Tests    ${EMPTY}    standard_libraries/operating_system/env_vars.robot
    [Teardown]    Remove Environment Variable    NON_ASCII_BY_RUNNER

*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    keywords/dynamic_positional_only_args.robot
Resource          atest_resource.robot

*** Test Cases ***
One Argument
    Check Test Case    ${TESTNAME}

Three arguments
    Check Test Case    ${TESTNAME}

Pos and named
    Check Test Case    ${TESTNAME}

Pos and names too few arguments
    Check Test Case    ${TESTNAME}

Three arguments too many arguments
    Check Test Case    ${TESTNAME}

Pos with default
    Check Test Case    ${TESTNAME}

All args
    Check Test Case    ${TESTNAME}

Too many markers
    Validate invalid arg spec error    0
    ...    Too many markers
    ...    Too many positional-only separators.

After varargs
    Validate invalid arg spec error    1
    ...    After varargs
    ...    Positional-only separator must be before named-only arguments.

After named-only marker
    Validate invalid arg spec error    2
    ...    After named-only marker
    ...    Positional-only separator must be before named-only arguments.

After kwargs
    Validate invalid arg spec error    3
    ...    After kwargs
    ...    Only last argument can be kwargs.

*** Keywords ***
Validate invalid arg spec error
    [Arguments]    ${index}    ${name}    ${error}
    Error in library
    ...    DynamicPositionalOnly
    ...    Adding keyword '${name}' failed: Invalid argument specification: ${error}
    ...    index=${index}

*** Settings ***
Suite Setup     Run Tests  ${EMPTY}  test_libraries/dynamic_libraries_with_invalid_argspec.robot
Resource        atest_resource.robot

*** Test Cases ***
Argspec consists of something else than strings
    Error message should be correct    0    argspec with other than strings
    ...    Calling dynamic method 'get_keyword_arguments' failed: Return value must be list of strings.

Argspec has named arguments before positional
    Invalid argument spec    1    named args before positional
    ...     Non-default argument after default arguments.

Argspec has multiple varargs
    Invalid argument spec    2    multiple varargs
    ...    Cannot have multiple varargs.

Argspec has kwargs before positional arguments
    Invalid argument spec    3    kwargs before positional args
    ...    Only last argument can be kwargs.

Argspec has kwargs before named arguments
    Invalid argument spec    4    kwargs before named args
    ...    Only last argument can be kwargs.

Argspec has kwargs before varargs
    Invalid argument spec    5    kwargs before varargs
    ...    Only last argument can be kwargs.

Keywords with valid arg spec can be used
    Check Test Case    ${TESTNAME}

*** Keywords ***
Error message should be correct
    [Arguments]    ${index}    ${kw}    ${msg}
    Check Test Case    ${TESTNAME}
    Check Log Message    ${ERRORS[${index}]}
    ...    Adding keyword '${kw}' to library 'InvalidArgSpecs' failed: ${msg}
    ...    ERROR

Invalid argument spec
    [Arguments]    ${index}    ${kw}    ${msg}
    Error message should be correct    ${index}    ${kw}
    ...    Invalid argument specification: ${msg}

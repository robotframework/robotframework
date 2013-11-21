*** Settings ***
Suite Setup     Run Tests  ${EMPTY}  test_libraries/dynamic_libraries_with_invalid_argspec.txt
Force Tags      regression  jybot  pybot
Resource        atest_resource.txt

*** Test Cases ***
Argspec consists of something else than strings
    Error message should be correct    0    argspec with other than strings
    ...    Calling dynamic method 'get_keyword_arguments' failed: Return value must be list of strings.

Argspec has named arguments before positional
    Error message should be correct    1    named args before positional
    ...     Non-default argument after default arguments.

Argspec has varargs before positional arguments
    Error message should be correct    2    varargs before positional args
    ...    Positional argument after varargs.

Argspec has varargs before named arguments
    Error message should be correct    3    varargs before named args
    ...    Positional argument after varargs.

Argspec has kwargs before positional arguments
    Error message should be correct    4    kwargs before positional args
    ...    Only last argument can be kwargs.

Argspec has kwargs before named arguments
    Error message should be correct    5    kwargs before named args
    ...    Only last argument can be kwargs.

Argspec has kwargs before varargs
    Error message should be correct    6    kwargs before varargs
    ...    Only last argument can be kwargs.

Keywords with valid arg spec can be used
    Check Test Case

*** Keywords ***
Error message should be correct
    [Arguments]    ${index}    ${kw}    ${msg}
    Check Test Case    ${TESTNAME}
    Check Log Message    ${ERRORS[${index}]}    Adding keyword '${kw}' to library 'InvalidArgSpecs' failed: ${msg}    WARN

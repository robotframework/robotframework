*** Settings ***
Suite Setup     Run Tests    ${EMPTY}    test_libraries/dynamic_libraries_with_invalid_argspec.robot
Resource        atest_resource.robot

*** Test Cases ***
Argspec consists of something else than strings
    Error message should be correct    0    other than strings
    ...    Calling dynamic method 'get_keyword_arguments' failed:
    ...    Return value must be a list of strings or non-empty tuples, got list.

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

Empty tuple in argspec
    Error message should be correct    6    empty tuple
    ...    Calling dynamic method 'get_keyword_arguments' failed:
    ...    Return value must be a list of strings or non-empty tuples, got list.

Too long tuple in argspec
    Invalid argument spec    7    too long tuple
    ...    Invalid argument "('too', 'long', 'tuple')".

Too long tuple in argspec with *varargs and **kwags
    Invalid argument spec    8    too long tuple with *varargs
    ...    Invalid argument "('*too', 'long')".
    Invalid argument spec    9    too long tuple with **kwargs
    ...    Invalid argument "('**too', 'long')".

Tuple with non-string first value
    Invalid argument spec    10    tuple with non-string first value
    ...    Invalid argument "(None,)".

Keywords with valid arg spec can be used
    Check Test Case    ${TESTNAME}

*** Keywords ***
Error message should be correct
    [Arguments]    ${index}    ${kw}    @{message}
    Check Test Case    ${TESTNAME}
    Error In Library    InvalidArgSpecs
    ...    Adding keyword '${kw}' failed:
    ...    @{message}
    ...    index=${index}

Invalid argument spec
    [Arguments]    ${index}    ${kw}    @{message}
    Error message should be correct    ${index}    ${kw}
    ...    Invalid argument specification:
    ...    @{message}

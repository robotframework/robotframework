*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    keywords/type_conversion/custom_converters.robot
Resource          atest_resource.robot

*** Test Cases ***
New conversion
    Check Test Case    ${TESTNAME}

Override existing conversion
    Check Test Case    ${TESTNAME}

Subclasses
    Check Test Case    ${TESTNAME}

Class as converter
    Check Test Case    ${TESTNAME}

Custom in Union
    Check Test Case    ${TESTNAME}

Accept subscripted generics
    Check Test Case    ${TESTNAME}

Failing conversion
    Check Test Case    ${TESTNAME}

Invalid converters
    Check Test Case    ${TESTNAME}
    Validate Errors
    ...    Custom converters must be callable, converter for Invalid is integer.
    ...    Custom converters must accept exactly one positional argument, converter 'TooFewArgs' accepts 0.
    ...    Custom converters must accept exactly one positional argument, converter 'TooManyArgs' accepts 2.
    ...    Custom converter 'KwOnlyNotOk' accepts keyword-only arguments which is not supported.
    ...    Custom converters must be specified using types, got string 'Bad'.

Non-type annotation
    Check Test Case    ${TESTNAME}

Using library decorator
    Check Test Case    ${TESTNAME}

Invalid converter dictionary
    Check Test Case    ${TESTNAME}
    Check Log Message    ${ERRORS}[-1]
    ...    Error in library 'InvalidCustomConverters': Argument converters must be given as a dictionary, got integer.
    ...    ERROR

*** Keywords ***
Validate Errors
    [Arguments]    @{messages}
    FOR    ${err}    ${msg}    IN ZIP    ${ERRORS}    ${messages}
        Check Log Message    ${err}    Error in library 'CustomConverters': ${msg}    ERROR
    END

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

With generics
    Check Test Case    ${TESTNAME}

With TypedDict
    Check Test Case    ${TESTNAME}

Failing conversion
    Check Test Case    ${TESTNAME}

`None` as strict converter
    Check Test Case    ${TESTNAME}

Only vararg
    Check Test Case    ${TESTNAME}

With library as argument to converter
    Check Test Case    ${TESTNAME}

Test scope library instance is reset between test
    Check Test Case    ${TESTNAME} 1
    Check Test Case    ${TESTNAME} 2

Global scope library instance is not reset between test
    Check Test Case    ${TESTNAME} 1
    Check Test Case    ${TESTNAME} 2

Invalid converters
    Check Test Case    ${TESTNAME}
    Validate Errors
    ...    Custom converters must be callable, converter for Invalid is integer.
    ...    Custom converters must accept one positional argument, 'TooFewArgs' accepts none.
    ...    Custom converters cannot have more than two mandatory arguments, 'TooManyArgs' has 'one', 'two' and 'three'.
    ...    Custom converters must accept one positional argument, 'NoPositionalArg' accepts none.
    ...    Custom converters cannot have mandatory keyword-only arguments, 'KwOnlyNotOk' has 'another' and 'kwo'.
    ...    Custom converters must be specified using types, got string 'Bad'.

Non-type annotation
    Check Test Case    ${TESTNAME}

Using library decorator
    Check Test Case    ${TESTNAME}

With embedded arguments
    Check Test Case    ${TESTNAME}

Failing conversion with embedded arguments
    Check Test Case    ${TESTNAME}

With dynamic library
    Check Test Case    ${TESTNAME}

Failing conversion with dynamic library
    Check Test Case    ${TESTNAME}

Invalid converter dictionary
    Check Test Case    ${TESTNAME}
    Check Log Message    ${ERRORS}[-1]
    ...    Error in library 'InvalidCustomConverters': Argument converters must be given as a dictionary, got integer.
    ...    ERROR

*** Keywords ***
Validate Errors
    [Arguments]    @{messages}
    FOR    ${err}    ${msg}    IN ZIP    ${ERRORS}    ${messages}    mode=SHORTEST
        Check Log Message    ${err}    Error in library 'CustomConverters': ${msg}    ERROR
    END

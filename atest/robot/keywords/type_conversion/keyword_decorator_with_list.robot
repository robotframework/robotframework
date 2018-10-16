*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    keywords/type_conversion/keyword_decorator_with_list.robot
Resource         atest_resource.robot

*** Test Cases ***
Basics
    Check Test Case    ${TESTNAME}

None means no type
    Check Test Case    ${TESTNAME}

Less types than arguments is ok
    Check Test Case    ${TESTNAME}

More types than arguments causes error
    Check Test Case    ${TESTNAME}
    ${error} =    Catenate
    ...    Adding keyword 'too_many_types' to library 'KeywordDecoratorWithList' failed:
    ...    Type information given to 2 arguments but keyword has only 1 argument.
    Check Log Message    ${ERRORS[0]}    ${error}    ERROR

Varargs and kwargs
    Check Test Case    ${TESTNAME}

Kwonly
    [Tags]    require-py3
    Check Test Case    ${TESTNAME}

Kwonly with kwargs
    [Tags]    require-py3
    Check Test Case    ${TESTNAME}

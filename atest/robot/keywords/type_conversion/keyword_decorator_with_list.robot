*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    keywords/type_conversion/keyword_decorator_with_list.robot
Resource         atest_resource.robot

*** Test Cases ***
Basics
    Check Test Case    ${TESTNAME}

None means no type
    Check Test Case    ${TESTNAME}

Falsy types mean no type
    Check Test Case    ${TESTNAME}

NoneType
    Check Test Case    ${TESTNAME}

None as string is None
    Check Test Case    ${TESTNAME}

None in tuple is alias for NoneType
    Check Test Case    ${TESTNAME}

Less types than arguments is ok
    Check Test Case    ${TESTNAME}

More types than arguments causes error
    Check Test Case    ${TESTNAME}
    Error In Library    KeywordDecoratorWithList
    ...    Adding keyword 'too_many_types' failed:
    ...    Type information given to 2 arguments but keyword has only 1 argument.

Varargs and kwargs
    Check Test Case    ${TESTNAME}

Kwonly
    Check Test Case    ${TESTNAME}

Kwonly with kwargs
    Check Test Case    ${TESTNAME}

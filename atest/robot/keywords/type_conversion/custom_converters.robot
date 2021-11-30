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

Failing conversion
    Check Test Case    ${TESTNAME}

Invalid converter
    Check Test Case    ${TESTNAME}

Non-type annotation
    Check Test Case    ${TESTNAME}

Using library decorator
    Check Test Case    ${TESTNAME}

Invalid converter dictionary
    Check Test Case    ${TESTNAME}
    Check Log Message    ${ERRORS}[0]
    ...    Error in library 'InvalidCustomConverters': Argument converters must be given as a dictionary, got integer.
    ...    ERROR

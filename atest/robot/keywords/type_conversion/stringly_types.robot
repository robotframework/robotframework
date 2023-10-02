*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    keywords/type_conversion/stringly_types.robot
Resource          atest_resource.robot

*** Test Cases ***
Parameterized list
    Check Test Case    ${TESTNAME}

Parameterized dict
    Check Test Case    ${TESTNAME}

Parameterized set
    Check Test Case    ${TESTNAME}

Parameterized tuple
    Check Test Case    ${TESTNAME}

Homogenous tuple
    Check Test Case    ${TESTNAME}

Union
    Check Test Case    ${TESTNAME}

Nested
    Check Test Case    ${TESTNAME}

Aliases
    Check Test Case    ${TESTNAME}

Invalid
    Check Test Case    ${TESTNAME}
    Check Log Message    ${ERRORS[0]}
    ...    Error in library 'StringlyTypes': Adding keyword 'invalid' failed: Parsing type 'bad[info' failed: Error at end: Closing ']' missing.
    ...    ERROR

*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    keywords/type_conversion/internal_conversion_using_typeinfo.robot
Resource          atest_resource.robot

*** Test Cases ***
Internal conversion
    Check Test Case    ${TESTNAME}

Custom converters
    Check Test Case    ${TESTNAME}

Language configuration
    Check Test Case    ${TESTNAME}

Default language configuration
    Check Test Case    ${TESTNAME}

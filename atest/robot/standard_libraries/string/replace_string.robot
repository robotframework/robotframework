*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    standard_libraries/string/replace_string.robot
Resource          atest_resource.robot

*** Test Cases ***
Replace String
    Check Test Case    ${TESTNAME}

Replace String Not Found
    Check Test Case    ${TESTNAME}

Replace String With Empty String
    Check Test Case    ${TESTNAME}

Replace String With Count 0
    Check Test Case    ${TESTNAME}

Replace String With Invalid Count
    Check Test Case    ${TESTNAME}

Replace String Using Regexp
    Check Test Case    ${TESTNAME}

Replace String Using Regexp With Count 0
    Check Test Case    ${TESTNAME}

Replace String Using Regexp Not Found
    Check Test Case    ${TESTNAME}

Replace String Using Regexp When Count Is Invalid
    Check Test Case    ${TESTNAME}


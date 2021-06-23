*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    standard_libraries/string/split_string.robot
Resource          atest_resource.robot

*** Test Cases ***
Split String
    Check Test Case    ${TESTNAME}

Split String With Longer Separator
    Check Test Case    ${TESTNAME}

Split String With none As Separator
    Check Test Case    ${TESTNAME}

Split String With Whitespaces and Separator Is None
    Check Test Case    ${TESTNAME}

Split String With Max Split 0
    Check Test Case    ${TESTNAME}

Split String With Max Split 1
    Check Test Case    ${TESTNAME}

Split String With Empty Separator
    Check Test Case    ${TESTNAME}

Split String With Empty String
    Check Test Case    ${TESTNAME}

Split String Separator not Found
    Check Test Case    ${TESTNAME}

Split String With Invalid Max Split
    Check Test Case    ${TESTNAME}

Split String From Right
    Check Test Case    ${TESTNAME}

Split String From Right With Longer Separator
    Check Test Case    ${TESTNAME}

Split String From Right With none As Separator
    Check Test Case    ${TESTNAME}

Split String From Right With Whitespaces and Separator Is None
    Check Test Case    ${TESTNAME}

Split String From Right With Max Split 0
    Check Test Case    ${TESTNAME}

Split String From Right With Max Split 1
    Check Test Case    ${TESTNAME}

Split String From Right With Empty Separator
    Check Test Case    ${TESTNAME}

Split String From Right With Empty String
    Check Test Case    ${TESTNAME}

Split String From Right Separator not Found
    Check Test Case    ${TESTNAME}

Split String From Right With Invalid Max Split
    Check Test Case    ${TESTNAME}

Split String To Characters
    Check Test Case    ${TESTNAME}

Split Empty String To Characters
    Check Test Case    ${TESTNAME}


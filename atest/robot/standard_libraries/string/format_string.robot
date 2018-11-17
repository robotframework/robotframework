*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    standard_libraries/string/format_string.robot
Resource          atest_resource.robot

*** Test Cases ***
Format String With Positional Argument
    Check Test Case    ${TESTNAME}

Format String With Positional Arguments
    Check Test Case    ${TESTNAME}

Format String With Named Search Replace Argument
    Check Test Case    ${TESTNAME}

Format String With Named Search Replace Arguments
    Check Test Case    ${TESTNAME}

Format String With Named And Search Replace Arguments
    Check Test Case    ${TESTNAME}

Format String From Non-ASCII Template
    Check Test Case    ${TESTNAME}

Format String From Template File
    Check Test Case    ${TESTNAME}

Format String From Template Non-ASCII File
    Check Test Case    ${TESTNAME}

Format String From Trailling Whitespace Template File
    Check Test Case    ${TESTNAME}

Attribute access
    Check Test Case    ${TESTNAME}

Item access
    Check Test Case    ${TESTNAME}

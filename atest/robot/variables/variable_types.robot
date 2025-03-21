*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    variables/variable_types.robot
Resource          atest_resource.robot

*** Test Cases ***
Variable section
    Check Test Case    ${TESTNAME}

Variables with invalid values or types
    Check Test Case    ${TESTNAME}

VAR syntax
    Check Test Case    ${TESTNAME}

Invalid VAR syntax value as scalar
    Check Test Case    ${TESTNAME}

Invalid VAR syntax type as scalar
    Check Test Case    ${TESTNAME}

Single variable assignment
    Check Test Case    ${TESTNAME}

Invalid value single variable assignment
    Check Test Case    ${TESTNAME}

Invalid type single variable assignment
    Check Test Case    ${TESTNAME}

Invalid type single variable assignment as list
    Check Test Case    ${TESTNAME}

Invalid type single variable assignment from scalar to list
    Check Test Case    ${TESTNAME}

Invalid type single variable assignment from scalar to dictionary
    Check Test Case    ${TESTNAME}

Multi variable assignment
    Check Test Case    ${TESTNAME}

Assignment
    Check Test Case    ${TESTNAME}

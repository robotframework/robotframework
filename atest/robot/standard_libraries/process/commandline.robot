*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    standard_libraries/process/commandline.robot
Resource         atest_resource.robot

*** Test Cases ***
Command line to list basics
    Check Test Case    ${TESTNAME}

Command line to list with internal quotes
    Check Test Case    ${TESTNAME}

Command line to list with unbalanced quotes
    Check Test Case    ${TESTNAME}

Command line to list with escaping
    Check Test Case    ${TESTNAME}

List to commandline basics
    Check Test Case    ${TESTNAME}

List to commandline with internal quotes
    Check Test Case    ${TESTNAME}

List to commandline with escaping
    Check Test Case    ${TESTNAME}

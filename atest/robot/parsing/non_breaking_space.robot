*** Settings ***
Documentation  Can be removed in RF 3.2 in favor of non_ascii_spaces.robot
Suite Setup    Run Tests    ${EMPTY}    parsing/nbsp.*
Resource       atest_resource.robot

*** Test Cases ***
Non-breaking spaces in plain text file
    Check test case  ${TESTNAME}

Non-breaking spaces in plain text file with pipes
    Check test case  ${TESTNAME}

Non-breaking spaces in TSV file
    Check test case  ${TESTNAME}

Non-breaking spaces in HTML file
    Check test case  ${TESTNAME}

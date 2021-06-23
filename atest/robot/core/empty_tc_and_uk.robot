*** Settings ***
Documentation   Empty test cases and user keywords
Suite Setup     Run Tests  ${EMPTY}  core/empty_testcase_and_uk.robot
Resource        atest_resource.robot

*** Test Cases ***
Test Case Without Name
    Check Test Case  ${EMPTY}

Empty Test Case
    Check Test Case  ${TESTNAME}

Empty Test Case With Setup And Teardown
    Check Test Case  ${TESTNAME}

Empty User Keyword
    Check Test Case  ${TESTNAME}

User Keyword With Only Non-Empty [Return] Works
    Check Test Case  ${TESTNAME}

User Keyword With Empty [Return] Does Not Work
    Check Test Case  ${TESTNAME}

Empty User Keyword With Other Settings Than [Return]
    Check Test Case  ${TESTNAME}

Non-Empty And Empty User Keyword
    Check Test Case  ${TESTNAME}

Non-Empty UK Using Empty UK
    Check Test Case  ${TESTNAME}

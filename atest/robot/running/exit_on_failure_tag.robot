*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    running/exit_on_failure_tag.robot
Resource          atest_resource.robot

*** Test Cases ***
Passing test with the tag has not special effect
    Check Test Case    ${TESTNAME}

Failing test without the tag has no special effect
    Check Test Case    ${TESTNAME}

Failing test with the tag initiates exit-on-failure
    Check Test Case    ${TESTNAME}

Subsequent tests are not run
    Check Test Case    ${TESTNAME} 1
    Check Test Case    ${TESTNAME} 2

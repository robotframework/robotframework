*** Settings ***
Resource          while.resource
Suite Setup       Run Tests    ${EMPTY}    running/while/nested_while.robot

*** Test Cases ***
Inside FOR
    ${tc}=    Check test case    ${TEST NAME}
    Check loop attributes    ${tc.body[0].body[0].body[0]}     PASS    4
    Check loop attributes    ${tc.body[0].body[1].body[0]}     PASS    3
    Check loop attributes    ${tc.body[0].body[2].body[0]}     PASS    2
    Length should be     ${tc.body[0].body}     3

Failing inside FOR
    ${tc}=    Check test case    ${TEST NAME}
    Check loop attributes    ${tc.body[0].body[0].body[0]}     FAIL    2
    Length should be     ${tc.body[0].body}     1

Inside IF
    ${tc}=    Check test case    ${TEST NAME}
    Check loop attributes    ${tc.body[0].body[0].body[1]}     PASS    4

In suite setup
    ${suite}=    Get Test Suite     Nested While
    Check loop attributes    ${suite.setup.body[1]}     PASS    4

In suite teardown
    ${suite}=    Get Test Suite     Nested While
    Check loop attributes    ${suite.teardown.body[1]}     PASS    4

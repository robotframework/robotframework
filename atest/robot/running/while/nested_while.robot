*** Settings ***
Resource          while.resource
Suite Setup       Run Tests    ${EMPTY}    running/while/nested_while.robot

*** Test Cases ***
Inside FOR
    ${tc}=    Check test case    ${TEST NAME}
    Check loop attributes    ${tc[0, 0, 0]}     PASS    4
    Check loop attributes    ${tc[0, 1, 0]}     PASS    3
    Check loop attributes    ${tc[0, 2, 0]}     PASS    2
    Length should be     ${tc[0].body}     3

Failing inside FOR
    ${tc}=    Check test case    ${TEST NAME}
    Check loop attributes    ${tc[0, 0, 0]}     FAIL    2
    Length should be     ${tc[0].body}     1

Inside IF
    ${tc}=    Check test case    ${TEST NAME}
    Check loop attributes    ${tc[0, 0, 1]}     PASS    4

In suite setup
    ${suite}=    Get Test Suite     Nested While
    Check loop attributes    ${suite.setup[1]}     PASS    4

In suite teardown
    ${suite}=    Get Test Suite     Nested While
    Check loop attributes    ${suite.teardown[1]}     PASS    4

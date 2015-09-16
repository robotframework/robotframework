*** Settings ***
Documentation   Testing pre/post condition is synonym to setup/teardown
Suite Setup     Run Tests  ${EMPTY}  core/setting_synonyms.robot
Resource        atest_resource.robot

*** Test Cases ***
Suite Precondition
    Check Log Message  ${SUITE.setup.msgs[0]}  Suite Precondition

Suite Postcondition
    Check Log Message  ${SUITE.teardown.msgs[0]}  Suite Postcondition

Test Precondition
    ${test} =  Check Test Case  Pre and Post Condition from Setting Table
    Check Log Message  ${test.setup.msgs[0]}  Test Precondition from Setting table

Test Postcondition
    ${test} =  Check Test Case  Pre and Post Condition from Setting Table
    Check Log Message  ${test.teardown.msgs[0]}  Test Postcondition from Setting table

Preconditon
    ${test} =  Check Test Case  Pre and Post Condition for Test
    Check Log Message  ${test.setup.msgs[0]}  Precondition for test

Postcondition
    ${test} =  Check Test Case  Pre and Post Condition for Test
    Check Log Message  ${test.teardown.msgs[0]}  Postcondition for test

Using Setup And Teardown With Test Pre And Post Condition
    ${test} =  Check Test Case  Overriding Pre and Post conditions With Setup And teardown
    Check Log Message  ${test.setup.msgs[0]}  Setup for test
    Should be Equal  ${test.teardown}  ${None}


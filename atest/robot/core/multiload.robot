*** Settings ***
Suite Setup     Run Tests    ${EMPTY}    core/multiload.robot
Resource        atest_resource.robot
*** Test Cases ***
Load the same library multiple times using different parameters
    Check Test Case    ${TESTNAME}

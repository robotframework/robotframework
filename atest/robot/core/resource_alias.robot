*** Settings ***
Suite Setup        Run Tests    ${EMPTY}    core/resource_alias.robot
Resource           atest_resource.robot

*** Test Cases ***
Resource Import With Alias
    Check Test Case    ${TEST NAME}

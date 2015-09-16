*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    running/dynamic_teardown.robot
Resource          atest_resource.robot

*** Test cases ***
Setting teardowns with variables dynamically
     Check test case   ${TEST NAME}

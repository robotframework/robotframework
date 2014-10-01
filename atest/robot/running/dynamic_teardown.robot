*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    running/dynamic_teardown.robot
Force Tags        regression
Default Tags      pybot    jybot
Resource          atest_resource.robot

*** Test cases ***
Setting teardowns with variables dynamically
     Check test case   ${TEST NAME}

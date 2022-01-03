*** Settings ***
Resource          while_resource.robot
Suite Setup       Run Tests    ${EMPTY}    running/while/invalid_while.robot
Test Template     Check test case

*** Test Cases ***
While without END
    ${TEST NAME}

While without condition
    ${TEST NAME}

While with multiple conditions
    ${TEST NAME}

While without body
    ${TEST NAME}

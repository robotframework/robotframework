*** Settings ***
Resource          atest_resource.robot
Suite Setup       Run Tests    ${EMPTY}    running/try-except/try-except.robot

*** Test Cases ***
Try with no failures
    Check Test Case    ${TEST NAME}

Try with first except executed
    Check Test Case    ${TEST NAME}

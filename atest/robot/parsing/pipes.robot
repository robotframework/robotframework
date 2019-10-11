*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    parsing/pipes.robot
Resource          atest_resource.robot

*** Test Cases ***
Minimum Pipes
    Check Test Case    ${TEST NAME}

Pipes All Around
    Check Test Case    ${TEST NAME}

Empty line with pipe
    Should Be True    not any(e.level == 'ERROR' for e in $ERRORS)
    Check Test Case    ${TEST NAME}

Pipes In Data
    Check Test Case    ${TEST NAME}

Extra Pipes At The End
    Check Test Case    ${TEST NAME}

Empty Cells In Middle
    Check Test Case    ${TEST NAME}

Consecutive spaces
    Check Test Case  ${TEST NAME}

Tabs
    Check Test Case  ${TEST NAME}

Using FOR Loop With Pipes
    Check Test Case  ${TEST NAME}

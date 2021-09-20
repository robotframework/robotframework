*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    parsing/pipes.robot
Resource          atest_resource.robot

*** Test Cases ***
Minimum Pipes
    Check Test Case    ${TEST NAME}

Pipes All Around
    Check Test Case    ${TEST NAME}

Empty line with pipe
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

Leading pipe without space after
    Check Test Case  |${TEST NAME}
    Check Test Case  ||
    Error In File    0    parsing/pipes.robot    6    Non-existing setting '||'.
    Error In File    1    parsing/pipes.robot    7    Non-existing setting '|Documentation'. Did you mean:\n${SPACE*4}Documentation
    Length Should Be    ${ERRORS}    2

*** Settings ***
Suite Setup     Run Tests  ${EMPTY}  parsing/data_formats/txt_special_cases
Resource        atest_resource.robot

*** Test Cases ***
Escaping Pipe
    Check Test Case  ${TEST NAME}

Using " In Data
    Check Test Case  ${TEST NAME}

Minimum Spaces
    Check Test Case  ${TEST NAME}

Spaces All Around
    Check Test Case  ${TEST NAME}

Extra Spaces At The End
    Check Test Case  ${TEST NAME}

Using FOR Loop With Spaces
    Check Test Case  ${TEST NAME}

Minimum Pipes
    Check Test Case  ${TEST NAME}

Pipes All Around
    Check Test Case  ${TEST NAME}

Empty line with pipe
    Stderr Should Be Empty
    Check Test Case  ${TEST NAME}

Pipes In Data
    Check Test Case  ${TEST NAME}

Extra Pipes At The End
    Check Test Case  ${TEST NAME}

Empty Cells In Middle
    Check Test Case  ${TEST NAME}

Using FOR Loop With Pipes
    Check Test Case  ${TEST NAME}

Tabs In Txt File
    ${tc} =  Check Test Case  Test With Tabs
    Check Log Message  ${tc.kws[0].msgs[0]}  I ignore tabs  DEBUG


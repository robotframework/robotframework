*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    standard_libraries/builtin/misc.robot
Resource          atest_resource.robot

*** Test Cases ***
No Operation
    Check Test Case    ${TEST NAME}

Catenate
    Check Test Case    ${TEST NAME}

Comment
    ${tc} =    Check Test Case    ${TEST NAME}
    Should Be Empty    ${tc[0].body}
    Should Be Empty    ${tc[1].body}
    Should Be Empty    ${tc[2].body}

Regexp Escape
    Check Test Case    ${TEST NAME}

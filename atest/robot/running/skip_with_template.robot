*** Settings ***
Suite Setup     Run Tests    ${EMPTY}    running/skip_with_template.robot
Resource        atest_resource.robot

*** Test Cases ***
Skip With Pass
    ${tc} =    Check Test Case    ${TEST NAME}
    Should Be Equal    ${tc.body[0].status}    SKIP
    Should Be Equal    ${tc.body[1].status}    PASS

Skip With Fail
    ${tc} =    Check Test Case    ${TEST NAME}
    Should Be Equal    ${tc.body[0].status}    PASS
    Should Be Equal    ${tc.body[1].status}    SKIP
    Should Be Equal    ${tc.body[2].status}    PASS
    Should Be Equal    ${tc.body[3].status}    SKIP
    Should Be Equal    ${tc.body[4].status}    FAIL

All Skips
    ${tc} =    Check Test Case    ${TEST NAME}
    Should Be Equal    ${tc.body[0].status}    SKIP
    Should Be Equal    ${tc.body[1].status}    SKIP

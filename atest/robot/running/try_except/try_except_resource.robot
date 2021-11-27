*** Settings ***
Resource          atest_resource.robot
Library           Collections


*** Keywords ***
Block statuses should be
    [Arguments]    @{statuses}
    ${tc} =    Check Test Case    ${TESTNAME}
    IF    'FAIL' in $statuses[1:] or ($statuses[0] == 'FAIL' and 'PASS' not in $statuses[1:])
        Should Be Equal    ${tc.body[0].status}    FAIL
    ELSE
        Should Be Equal    ${tc.body[0].status}    PASS
    END
    ${blocks}=    Create list    ${tc.body[0].try_block}    @{tc.body[0].except_blocks}
    IF     ${tc.body[0].else_block.body}    Append to list    ${blocks}    ${tc.body[0].else_block}
    IF     ${tc.body[0].finally_block.body}    Append to list    ${blocks}    ${tc.body[0].finally_block}
    ${expected_block_count}=    Get Length   ${statuses}
    Length Should Be    ${blocks}    ${expected_block_count}
    FOR    ${block}    ${status}    IN ZIP    ${blocks}    ${statuses}
        Should Be Equal    ${block.status}    ${status}
    END

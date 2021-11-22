*** Settings ***
Resource          atest_resource.robot


*** Keywords ***
Block statuses should be
    [Arguments]    @{statuses}
    ${tc} =    Check Test Case    ${TESTNAME}
    IF    'PASS' in $statuses[1:] or ($statuses[0] == 'PASS' and 'FAIL' not in $statuses[1:])
        Should Be Equal    ${tc.body[0].status}    PASS
    ELSE
        Should Be Equal    ${tc.body[0].status}    FAIL
    END
    ${blocks}=    Create list    ${tc.body[0].try_block}    @{tc.body[0].except_blocks}    #${tc.body[0].else_block}
    FOR    ${block}    ${status}    IN ZIP    ${blocks}    ${statuses}
        Should Be Equal    ${block.status}    ${status}
    END

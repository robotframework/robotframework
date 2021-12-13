*** Settings ***
Resource          atest_resource.robot
Library           Collections


*** Keywords ***
Verify try except and block statuses
    [Arguments]    @{statuses}    ${tc_status}=${None}
    ${tc}=    Check test status    @{statuses}    tc_status=${tc_status}
    Block statuses should be    ${tc.body[0]}    @{statuses}
    RETURN    ${tc}

Verify try except and block statuses in uk
    [Arguments]    @{statuses}    ${tc_status}=${None}
    ${tc}=    Check test status    @{statuses}    tc_status=${tc_status}
    Block statuses should be    ${tc.body[0].body[0]}    @{statuses}
    RETURN    ${tc}

Check Test Status
    [Arguments]    @{statuses}    ${tc_status}=${None}
    ${tc} =    Check Test Case    ${TESTNAME}
    IF    $tc_status != ${None}
        Should Be Equal    ${tc.body[0].status}    ${tc_status}
    ELSE IF    'FAIL' in $statuses[1:] or ($statuses[0] == 'FAIL' and 'PASS' not in $statuses[1:])
        Should Be Equal    ${tc.body[0].status}    FAIL
    ELSE
        Should Be Equal    ${tc.body[0].status}    PASS
    END
    RETURN    ${tc}

Block statuses should be
    [Arguments]    ${try_except}    @{statuses}
    ${blocks}=    Create list    ${try_except.try_block}    @{try_except.except_blocks}
    IF     ${try_except.else_block.body}    Append to list    ${blocks}    ${try_except.else_block}
    IF     ${try_except.finally_block.body}    Append to list    ${blocks}    ${try_except.finally_block}
    ${expected_block_count}=    Get Length   ${statuses}
    Length Should Be    ${blocks}    ${expected_block_count}
    FOR    ${block}    ${status}    IN ZIP    ${blocks}    ${statuses}
        Should Be Equal    ${block.status}    ${status}
    END

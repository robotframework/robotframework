*** Settings ***
Resource          atest_resource.robot
Library           Collections

*** Keywords ***
Verify try except and block statuses
    [Arguments]    @{types_and_statuses}    ${tc_status}=    ${path}=body[0]    ${pattern_types}=[]
    ${tc}=    Check test status    @{{[s.split(':')[-1] for s in $types_and_statuses]}}    tc_status=${tc_status}
    Block statuses should be    ${tc.${path}}    @{types_and_statuses}
    Pattern types should be    ${tc.${path}}    ${pattern_types}
    RETURN    ${tc}

Check Test Status
    [Arguments]    @{statuses}    ${tc_status}=${None}
    ${tc} =    Check Test Case    ${TESTNAME}
    IF    $tc_status
        Should Be Equal    ${tc.status}    ${tc_status}
    ELSE IF    'FAIL' in $statuses[1:] or ($statuses[0] == 'FAIL' and 'PASS' not in $statuses[1:])
        Should Be Equal    ${tc.status}    FAIL
    ELSE
        Should Be Equal    ${tc.status}    PASS
    END
    RETURN    ${tc}

Block statuses should be
    [Arguments]    ${try_except}    @{types_and_statuses}
    @{blocks}=    Set Variable    ${try_except.body}
    ${expected_block_count}=    Get Length    ${types_and_statuses}
    Length Should Be    ${blocks}    ${expected_block_count}
    FOR    ${block}    ${type_and_status}    IN ZIP    ${blocks}    ${types_and_statuses}
        IF    ':' in $type_and_status
            Should Be Equal    ${block.type}      ${type_and_status.split(':')[0]}
            Should Be Equal    ${block.status}    ${type_and_status.split(':')[1]}
        ELSE
            Should Be Equal    ${block.status}    ${type_and_status}
        END
    END

Pattern types should be
    [Arguments]    ${try_except}    ${pattern_types}
    @{pattern_types} =    Evaluate    ${pattern_types}
    FOR    ${except}    ${expected}    IN ZIP    ${try_except.body[1:]}    ${pattern_types}    mode=shortest
        Should Be Equal    ${except.type}    EXCEPT
        Should Be Equal    ${except.pattern_type}    ${expected}
    END

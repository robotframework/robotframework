*** Settings ***
Resource        atest_resource.robot

*** Keywords ***
Check IF/ELSE Status
    [Arguments]    @{statuses}    ${types}=${None}    ${root}=${None}    ${test}=${TEST NAME}    ${index}=0    ${else}=${True}    ${run}=${True}
    IF    not $root
        ${tc} =    Check Test Case    ${test}
        ${root} =    Set Variable    ${tc.body}[${index}]
    END
    Should Be Equal    ${root.type}    IF/ELSE ROOT
    IF    'FAIL' in ${statuses}
        Should Be Equal    ${root.status}    FAIL
    ELSE IF    ${run}
        Should Be Equal    ${root.status}    PASS
    ELSE
        Should Be Equal    ${root.status}    NOT RUN
    END
    Check Branch Statuses    ${root.body}    ${statuses}    ${types}    ${else}

Check Branch Statuses
    [Arguments]    ${branches}    ${statuses}    ${types}=${None}    ${else}=${True}
    IF   $types
        ${types} =    Evaluate    ${types}
    ELSE
        IF    ${else} and len($branches) > 1
            ${types} =    Evaluate    ['IF'] + ['ELSE IF'] * (len($branches) - 2) + ['ELSE']
        ELSE
            ${types} =    Evaluate    ['IF'] + ['ELSE IF'] * (len($branches) - 1)
        END
    END
    Should Be Equal    ${{len($branches)}}    ${{len($statuses)}}
    Should Be Equal    ${{len($branches)}}    ${{len($types)}}
    FOR    ${branch}    ${type}    ${status}    IN ZIP    ${branches}    ${types}    ${statuses}
        Should Be Equal    ${branch.type}    ${type}
        Should Be Equal    ${branch.status}    ${status}
    END

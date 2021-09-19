*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    running/if/else_if.robot
Test Template     Check IF/ELSE Status
Resource          atest_resource.robot

*** Test Cases ***
Else if condition 1 passes
    PASS    NOT RUN    NOT RUN

Else if condition 2 passes
    NOT RUN    PASS    NOT RUN

Else if else passes
    NOT RUN    NOT RUN    PASS

Else if condition 1 failing
    FAIL    NOT RUN    NOT RUN

Else if condition 2 failing
    NOT RUN    FAIL    NOT RUN

Else if else failing
    NOT RUN    NOT RUN    FAIL

Invalid
    FAIL    NOT RUN

After failure
    NOT RUN    NOT RUN    NOT RUN    index=1

*** Keywords ***
Check IF/ELSE Status
    [Arguments]    @{statuses}    ${index}=0
    ${tc} =    Check Test Case    ${TESTNAME}
    ${if} =    Set Variable    ${tc.body}[${index}]
    IF    'FAIL' in ${statuses}
        Should Be Equal    ${if.status}    FAIL
    ELSE IF    'PASS' in ${statuses}
        Should Be Equal    ${if.status}    PASS
    ELSE
        Should Be Equal    ${if.status}    NOT RUN
    END
    Check Branch Statuses    ${if.body}    ${statuses}

Check Branch Statuses
    [Arguments]    ${branches}    ${statuses}
    ${types} =    Evaluate    ['IF'] + ['ELSE IF'] * (len($branches) - 2) + ['ELSE']
    Should Be Equal    ${{len($branches)}}    ${{len($statuses)}}
    Should Be Equal    ${{len($branches)}}    ${{len($types)}}
    FOR    ${branch}    ${type}    ${status}    IN ZIP    ${branches}    ${types}    ${statuses}
        Should Be Equal    ${branch.type}    ${type}
        Should Be Equal    ${branch.status}    ${status}
    END

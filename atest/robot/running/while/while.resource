*** Settings ***
Resource        atest_resource.robot

*** Keywords ***
Check WHILE loop
    [Arguments]    ${status}    ${iterations}    ${path}=body[0]    ${not_run}=False
    ${tc}=    Check test case    ${TEST NAME}
    ${loop}=    Check loop attributes     ${tc.${path}}    ${status}    ${iterations}
    IF    ${not_run}
        Should Be Equal    ${loop.body[0].status}    NOT RUN
    END
    RETURN    ${loop}

Check loop attributes
    [Arguments]    ${loop}    ${status}    ${iterations}
    Should be equal    ${loop.type}    WHILE
    Should be equal    ${loop.status}    ${status}
    IF    '${iterations}' != 'not known'
        Length Should Be    ${loop.kws}       ${iterations}
    END
    RETURN    ${loop}

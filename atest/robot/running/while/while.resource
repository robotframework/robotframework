*** Settings ***
Resource        atest_resource.robot

*** Keywords ***
Check WHILE loop
    [Arguments]    ${status}    ${iterations}    ${path}=body[0]    ${not_run}=False
    ${tc}=    Check Test Case    ${TEST NAME}
    ${loop}=    Check Loop Attributes     ${tc.${path}}    ${status}    ${iterations}
    IF    ${not_run}
        Should Be Equal    ${loop.body[0].status}    NOT RUN
    END
    RETURN    ${loop}

Check Loop Attributes
    [Arguments]    ${loop}    ${status}    ${iterations}
    Should Be Equal    ${loop.type}    WHILE
    Should Be Equal    ${loop.status}    ${status}
    IF    '${iterations}' != 'not known'
        Length Should Be    ${loop.non_messages}    ${iterations}
    END
    RETURN    ${loop}

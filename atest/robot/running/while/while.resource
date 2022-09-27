*** Settings ***
Resource        atest_resource.robot

*** Keywords ***
Check WHILE loop
    [Arguments]    ${status}    ${iterations}    ${path}=body[0]
    ${tc}=    Check test case    ${TEST NAME}
    ${loop}=    Check loop attributes     ${tc.${path}}    ${status}    ${iterations}
    RETURN    ${loop}

Check loop attributes
    [Arguments]    ${loop}    ${status}    ${iterations}
    Should be equal    ${loop.type}    WHILE
    Should be equal    ${loop.status}    ${status}
    Length Should Be    ${loop.kws}       ${iterations}
    RETURN    ${loop}

*** Settings ***
Resource    atest_resource.robot


*** Keywords ***
Check while loop
    [Arguments]    ${status}    ${iterations}
    ${tc}=    Check test case    ${TEST NAME}
    ${loop}=    Check loop attributes     ${tc.body[0]}    ${status}    ${iterations}
    RETURN    ${loop}

Check loop attributes
    [Arguments]    ${loop}    ${status}    ${iterations}
    Should be equal    ${loop.type}    WHILE
    Should be equal    ${loop.status}    ${status}
    Length Should Be    ${loop.kws}       ${iterations}
    RETURN    ${loop}

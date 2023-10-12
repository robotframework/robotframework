*** Settings ***
Resource          atest_resource.robot

*** Keywords ***
Check test and get loop
    [Arguments]    ${test name}    ${loop index}=0
    ${tc} =    Check Test Case    ${test name}
    RETURN    ${tc.body}[${loop index}]

Check test and failed loop
    [Arguments]    ${test name}    ${type}=FOR    ${loop index}=0    &{config}
    ${loop} =    Check test and get loop    ${test name}    ${loop index}
    Length Should Be    ${loop.body}    2
    Should Be Equal     ${loop.body[0].type}    ITERATION
    Should Be Equal     ${loop.body[1].type}    MESSAGE
    Run Keyword    Should Be ${type} loop    ${loop}    1    FAIL    &{config}

Should be FOR loop
    [Arguments]    ${loop}    ${iterations}    ${status}=PASS    ${flavor}=IN
    ...    ${start}=${None}    ${mode}=${None}    ${fill}=${None}
    Should Be Equal     ${loop.type}      FOR
    Should Be Equal     ${loop.flavor}    ${flavor}
    Should Be Equal     ${loop.start}     ${start}
    Should Be Equal     ${loop.mode}      ${mode}
    Should Be Equal     ${loop.fill}      ${fill}
    Length Should Be    ${loop.body.filter(messages=False)}    ${iterations}
    Should Be Equal     ${loop.status}    ${status}

Should be IN RANGE loop
    [Arguments]    ${loop}    ${iterations}    ${status}=PASS
    Should Be FOR Loop   ${loop}    ${iterations}    ${status}    IN RANGE

Should be IN ZIP loop
    [Arguments]    ${loop}    ${iterations}    ${status}=PASS    ${mode}=${None}    ${fill}=${None}
    Should Be FOR Loop   ${loop}    ${iterations}    ${status}    IN ZIP    mode=${mode}    fill=${fill}

Should be IN ENUMERATE loop
    [Arguments]    ${loop}    ${iterations}    ${status}=PASS    ${start}=${None}
    Should Be FOR Loop   ${loop}    ${iterations}    ${status}    IN ENUMERATE    start=${start}

Should be FOR iteration
    [Arguments]    ${iteration}    &{assign}
    Should Be Equal    ${iteration.type}    ITERATION
    Should Be Equal    ${iteration.assign}    ${assign}

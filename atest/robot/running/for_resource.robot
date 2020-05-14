*** Settings ***
Resource          atest_resource.robot

*** Keywords ***
Check test and get loop
    [Arguments]    ${test name}    ${loop index}=0
    ${tc} =    Check Test Case    ${test name}
    [Return]    ${tc.kws}[${loop index}]

Check test and failed loop
    [Arguments]    ${test name}    ${type}=FOR    ${loop index}=0
    ${loop} =    Check test and get loop    ${test name}    ${loop index}
    Run Keyword    Should Be ${type} loop    ${loop}    0   FAIL

Should be FOR loop
    [Arguments]    ${kw}    ${iterations}    ${status}=PASS
    Should Be Equal     ${kw.type}      for
    Should Contain      ${kw.name}      IN
    Length Should Be    ${kw.kws}       ${iterations}
    Should Be Equal     ${kw.status}    ${status}

Should be IN RANGE loop
    [Arguments]    ${kw}    ${iterations}    ${status}=PASS
    Should Be FOR Loop   ${kw}         ${iterations}    ${status}
    Should Contain       ${kw.name}    IN RANGE

Should be IN ZIP loop
    [Arguments]    ${kw}    ${iterations}    ${status}=PASS
    Should Be FOR loop    ${kw}    ${iterations}    ${status}
    Should Contain        ${kw.name}    IN ZIP

Should be IN ENUMERATE loop
    [Arguments]    ${kw}    ${iterations}    ${status}=PASS
    Should Be FOR loop    ${kw}    ${iterations}    ${status}
    Should Contain        ${kw.name}    IN ENUMERATE

Should be loop iteration
    [Arguments]    ${kw}    ${name}
    Should Be Equal    ${kw.type}    foritem
    Should Be Equal    ${kw.name}    ${name}

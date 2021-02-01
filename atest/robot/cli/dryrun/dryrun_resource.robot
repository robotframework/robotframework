*** Settings ***
Resource          atest_resource.robot

*** Keywords ***
Keyword should have been skipped with tag
    [Arguments]    ${kw}    ${name}    ${tags}
    Check Keyword Data    ${kw}    ${name}    status=PASS    tags=${tags}
    Should Be Empty    ${kw.kws}

Keyword should have been validated
    [Arguments]    ${kw}
    Check Keyword Data    ${kw}           resource.This is validated
    Check Keyword Data    ${kw.kws[0]}    BuiltIn.Log    status=NOT RUN    args=This is validated

Last keyword should have been validated
    ${tc} =    Get test case    ${TEST NAME}
    Keyword should have been validated    ${tc.kws[-1]}

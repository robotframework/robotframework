*** Settings ***
Resource          atest_resource.robot

*** Keywords ***
Keyword should have been skipped with tag
    [Arguments]    ${kw}    ${name}    ${tags}
    Check Keyword Data    ${kw}    ${name}    status=PASS    tags=${tags}    children=0

Keyword should have been validated
    [Arguments]    ${kw}
    Check Keyword Data    ${kw}       resource.This is validated
    Check Keyword Data    ${kw[0]}    BuiltIn.Log    status=NOT RUN    args=This is validated

Last keyword should have been validated
    ${tc} =    Get Test Case    ${TEST NAME}
    Keyword should have been validated    ${tc[-1]}

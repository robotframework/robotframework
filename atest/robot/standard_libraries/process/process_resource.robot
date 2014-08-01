*** Settings ***
Resource          atest_resource.robot

*** Keywords ***
Check Precondition
    ${tc} =    Get Test Case    ${TEST NAME}
    @{tags} =    Set Variable    ${tc.tags}
    Run Keyword If   'precondition-fail' in ${tags}
    ...    Fail    precondition fail    -regression

*** Settings ***
Resource          atest_resource.txt

*** Keywords ***
Check Precondition
    ${tc} =    Get Test Case    ${TEST NAME}
    @{tags} =    Set Variable    ${tc.tags}
    Run Keyword If   'precondition-fail' in ${tags}
    ...    Fail    precondition fail    -regression

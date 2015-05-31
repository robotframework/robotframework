*** Settings ***
Resource          atest_resource.robot

*** Variables ***
${TEST DATA}      misc/pass_and_fail.robot
${LOG}            %{TEMPDIR}/modified_log.html

*** Keywords ***
Output should be modified
    [Arguments]    @{added tags}
    Check Test Tags    Pass    force    pass    @{added tags}
    Length Should Be    ${SUITE.tests}    1

Output should not be modified
    Check Test Tags    Pass    force    pass
    Check Test Tags    Fail    force    fail
    Length Should Be    ${SUITE.tests}    2

Log should be modified
    [Arguments]    @{added tags}
    Log should contain strings    Hello says \\"Pass\\"!    force    pass    @{added tags}
    Log should not contain strings    Hello says \\"Fail\\"!    fail

Log should not be modified
    Log should contain strings    Hello says \\"Pass\\"!    Hello says \\"Fail\\"!
    Log should not contain strings    visited

Log should contain strings
    [Arguments]    @{strings}
    ${content} =    Get File    ${LOG}
    :FOR    ${string}    IN    @{strings}
    \    Should Contain    ${content}    "*${string}"

Log should not contain strings
    [Arguments]    @{strings}
    ${content} =    Get File    ${LOG}
    :FOR    ${string}    IN    @{strings}
    \    Should Not Contain    ${content}    "*${string}"

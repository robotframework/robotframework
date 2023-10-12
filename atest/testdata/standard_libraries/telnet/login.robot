*** Settings ***
Test Teardown     Close All Connections
Library           Telnet
Resource          telnet_resource.robot

*** Test Cases ***

Successful login without prompt
    Open Connection    ${HOST}
    Login and verify output

Successful login with prompt
    Open Connection    ${HOST}    prompt=${PROMPT}
    Login and verify output

Failed login without prompt
    [Documentation]    FAIL Login incorrect
    Open Connection    ${HOST}
    Login    invalid    password    login_timeout=5 seconds

Failed login with prompt
    [Documentation]    FAIL Login incorrect
    Open Connection    ${HOST}    timeout=5 seconds    prompt=${PROMPT}
    Login    ${USERNAME}    ${EMPTY}    login_prompt=:    password_prompt=:
    ...    login_timeout=Not used    login_incorrect=This is not used

*** Keywords ***
Login and verify output
    ${output} =    Login    ${USERNAME}    ${PASSWORD}
    Should Contain Once    ${output}    login: test\r\n
    Should Not Contain     ${output}    test\n
    Should Contain Once    ${output}    Password: \r\n
    Should Contain Once    ${output}    ${FULL PROMPT}
    Should End With        ${output}    ${FULL PROMPT}

Should Contain Once
    [Arguments]    ${output}    ${expected}
    Should Contain X Times    ${output}    ${expected}    1

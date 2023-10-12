*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    standard_libraries/telnet/login.robot
Resource          telnet_resource.robot

*** Test Cases ***

Successful login without prompt
    Verify successful login

Successful login with prompt
    Verify successful login

Failed login without prompt
    Verify failed login    invalid

Failed login with prompt
    Verify failed login    ${USERNAME}

*** Keywords ***
Verify successful login
    ${tc} =    Check Test Case    ${TEST NAME}
    ${output} =    Set Variable    ${tc.kws[1].kws[0].msgs[0].message}
    Should Contain Once    ${output}    login: test\n
    Should Contain Once    ${output}    Password: 
    Should Contain Once    ${output}    ${FULL PROMPT.strip()}
    Should End With        ${output}    ${FULL PROMPT.strip()}

Should Contain Once
    [Arguments]    ${output}    ${expected}
    Should Contain X Times    ${output}    ${expected}    1

Verify failed login
    [Arguments]     ${user}
    ${tc} =    Check Test Case    ${TEST NAME}
    ${output} =    Set Variable    ${tc.kws[1].msgs[0].message}
    Should Contain Once    ${output}    login: ${user}\n
    Should Contain Once    ${output}    Password: 
    Should Contain Once    ${output}    Login incorrect
    Should End With        ${output}    login:
    Should Not Contain     ${output}    ${PROMPT START}

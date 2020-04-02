*** Settings ***
Resource          rebot_resource.robot

*** Variables ***
${INPUTFILE}      %{TEMPDIR}${/}rebot-test-rmkw.xml

*** Keywords ***
Keyword Should Be Empty
    [Arguments]    ${kw}    ${name}    @{args}
    Check Keyword Name And Args    ${kw}    ${name}    @{args}
    Should Be Empty    ${kw.keywords}
    Should Be Empty    ${kw.messages}

Keyword Should Not Be Empty
    [Arguments]    ${kw}    ${name}    @{args}
    Check Keyword Name And Args    ${kw}    ${name}    @{args}
    ${num_keywords}=    Get Length    ${kw.keywords}
    ${num_messages}=    Get Length    ${kw.messages}
    Should Be True    ${num_keywords} + ${num_messages} > 0

Check Keyword Name And Args
    [Arguments]    ${kw}    ${name}    @{args}
    Should Be Equal    ${kw.name}    ${name}
    Lists Should Be Equal    ${kw.args}    ${args}

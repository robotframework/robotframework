*** Settings ***
Resource          rebot_resource.robot

*** Variables ***
${INPUTFILE}      %{TEMPDIR}${/}rebot-test-rmkw.xml
${DATA REMOVED}   <span class="robot-note">Content removed using the --remove-keywords option.</span>

*** Keywords ***
Keyword Should Be Empty
    [Arguments]    ${kw}    ${name}    @{args}
    Should End With    ${kw.message}    ${DATA REMOVED}
    Check Keyword Name And Args    ${kw}    ${name}    @{args}
    Should Be Empty    ${kw.body}

IF Branch Should Be Empty
    [Arguments]    ${branch}    ${type}    ${condition}=${None}
    Should Be Equal    ${branch.message}      *HTML* ${DATA REMOVED}
    Should Be Equal    ${branch.type}         ${type}
    Should Be Equal    ${branch.condition}    ${condition}
    Should Be Empty    ${branch.body}

FOR Loop Should Be Empty
    [Arguments]    ${loop}    ${flavor}
    Should Be Equal    ${loop.message}    *HTML* ${DATA REMOVED}
    Should Be Equal    ${loop.type}       FOR
    Should Be Equal    ${loop.flavor}     ${flavor}
    Should Be Empty    ${loop.body}

TRY Branch Should Be Empty
    [Arguments]    ${branch}    ${type}    ${message}=
    Should Be Equal    ${branch.message}    *HTML* ${message}${DATA REMOVED}
    Should Be Equal    ${branch.type}       ${type}
    Should Be Empty    ${branch.body}

Keyword Should Not Be Empty
    [Arguments]    ${kw}    ${name}    @{args}
    Check Keyword Name And Args    ${kw}    ${name}    @{args}
    ${num_keywords}=    Get Length    ${kw.kws}
    ${num_messages}=    Get Length    ${kw.messages}
    Should Be True    ${num_keywords} + ${num_messages} > 0

Check Keyword Name And Args
    [Arguments]    ${kw}    ${name}    @{args}
    Should Be Equal    ${kw.full_name}    ${name}
    Lists Should Be Equal    ${kw.args}    ${args}

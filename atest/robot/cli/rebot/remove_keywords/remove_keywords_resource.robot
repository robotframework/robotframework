*** Settings ***
Resource          rebot_resource.robot

*** Variables ***
${INPUTFILE}      %{TEMPDIR}${/}rebot-test-rmkw.xml

*** Keywords ***
Keyword Should Be Empty
    [Arguments]    ${kw}    ${name}    @{args}
    Should End With    ${kw.doc}    _Keyword data removed using --RemoveKeywords option._
    Check Keyword Name And Args    ${kw}    ${name}    @{args}
    Should Be Empty    ${kw.body}

IF Branch Should Be Empty
    [Arguments]    ${branch}    ${type}    ${condition}=${None}
    Should Be Equal    ${branch.doc}    _Keyword data removed using --RemoveKeywords option._
    Should Be Equal    ${branch.type}    ${type}
    Should Be Equal    ${branch.condition}    ${condition}
    Should Be Empty    ${branch.body}

FOR Loop Should Be Empty
    [Arguments]    ${loop}    ${flavor}
    Should Be Equal    ${loop.doc}    _Keyword data removed using --RemoveKeywords option._
    Should Be Equal    ${loop.type}    FOR
    Should Be Equal    ${loop.flavor}    ${flavor}
    Should Be Empty    ${loop.body}

Keyword Should Not Be Empty
    [Arguments]    ${kw}    ${name}    @{args}
    Check Keyword Name And Args    ${kw}    ${name}    @{args}
    ${num_keywords}=    Get Length    ${kw.kws}
    ${num_messages}=    Get Length    ${kw.messages}
    Should Be True    ${num_keywords} + ${num_messages} > 0

Check Keyword Name And Args
    [Arguments]    ${kw}    ${name}    @{args}
    Should Be Equal    ${kw.name}    ${name}
    Lists Should Be Equal    ${kw.args}    ${args}

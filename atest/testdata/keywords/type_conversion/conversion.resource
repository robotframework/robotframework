*** Keywords ***
Conversion Should Fail
    [Arguments]    ${kw}    @{args}    ${error}=    ${type}=${kw.lower()}    &{kwargs}
    ${arg} =    Evaluate    (list($args) + list($kwargs.values()))[0].replace('[', '?')
    ${end} =    Set Variable If    $error    : ${error}    .
    Run Keyword And Expect Error
    ...    ValueError: Argument 'argument' got value '${arg}' that cannot be converted to ${type}${end}
    ...    ${kw}    @{args}    &{kwargs}

Boolean, None, List and Dict are not converted
    [Arguments]    ${kw}
    Run Keyword    ${kw}    ${True}    ${True}
    Run Keyword    ${kw}    ${None}    ${None}
    Run Keyword    ${kw}    ${LIST}    ${LIST}
    Run Keyword    ${kw}    ${DICT}    ${DICT}

String None is converted to None object
    [Arguments]    ${kw}
    Run Keyword    ${kw}    None       ${None}
    Run Keyword    ${kw}    NONE       ${None}
    Run Keyword    ${kw}    none       ${None}

*** Keywords ***
Conversion Should Fail
    [Arguments]    ${kw}    @{args}    ${error}=    ${type}=${kw.lower()}    ${arg_type}=    &{kwargs}
    ${arg} =    Evaluate    (list($args) + list($kwargs.values()))[0]
    ${arg_type} =    Set Variable If    $arg_type    ${SPACE}(${arg_type})    ${EMPTY}
    ${end} =    Set Variable If    $error    : ${error}    .
    Run Keyword And Expect Error
    ...    ${{'GLOB' if '*' in $error else 'EQUALS'}}: ValueError: Argument 'argument' got value '${arg}'${arg_type} that cannot be converted to ${type}${end}
    ...    ${kw}    @{args}    &{kwargs}

String None is converted to None object
    [Arguments]    ${kw}
    Run Keyword    ${kw}    None       ${None}
    Run Keyword    ${kw}    NONE       ${None}
    Run Keyword    ${kw}    none       ${None}

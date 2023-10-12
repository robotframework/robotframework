*** Variables ***
${VERSION}      1.2

*** Test Cases ***
Normal name
    Normal name

Names are not formatted
    user_keyword nameS _are_not_ FORmatted
    User Keyword Names Are Not Formatted
    User keyword names are not formatted
    user keyword names are not formatted
    userkeywordnamesarenotformatted
    USERKEYWORDNAMESARENOTFORMATTED
    u_s_e_r_k_e_y_w_o_r_d_n_a_m_e_s_a_r_e_n_o_t_f_o_r_m_a_t_t_e_d
    U_S_E_R_K_E_Y_W_O_R_D_N_A_M_E_S_A_R_E_N_O_T_F_O_R_M_A_T_T_E_D

Documentation
    Documentation

Documentation in multiple columns
    Documentation in multiple columns

Documentation in multiple rows
    Documentation in multiple rows

Short doc consists of first logical, not physical, line
    Short doc consists of first logical, not physical, line

Documentation with variables
    Documentation with variables

Documentation with non-existing variables
    Documentation with non-existing variables

Documentation with unclosed variables
    Documentation with unclosed variables

Documentation with escaping
    Documentation with escaping

Arguments
    Arguments    mandatory
    Arguments    1    2
    Arguments    ${1}    ${2}    ${3}    ${4}    ${5}    key=${6}

Teardown
    Teardown

Teardown with variables
    Teardown with variables

Teardown with escaping
    Teardown with escaping

Return
    ${ret} =    Return
    Should Be Equal    ${ret}    Return value

Return using variables
    ${ret} =    Return using variables
    Should Be Equal    ${ret}    Return value 2

Return multiple
    ${r1}    ${r2}    ${r3}    ${r4}    ${r5} =    Return multiple    1    ${2}
    Should Be Equal    ${r1} ${r2} ${r3} ${r4} ${r5}    1 + 2 = 3

Return with escaping
    ${r1}    ${r2}    ${r3}    ${r4} =    Return with escaping
    Should Be Equal    ${r1}-${r2}-${r3}-${r4}    \${XXX}-c:\\temp--\\

Timeout
    Timeout

Timeout with variables
    Timeout with variables

Invalid timeout
    [Documentation]    FAIL Setting keyword timeout failed: Invalid time string 'invalid'.
    Invalid timeout

Multiple settings
    ${ret} =    Multiple settings    World
    Should Be Equal    ${ret}    Hello World!!

Invalid setting
    [Documentation]    FAIL Non-existing setting 'Invalid Setting'.
    Invalid
    Invalid

Setting not valid with user keywords
    [Documentation]    FAIL Setting 'Metadata' is not allowed with user keywords.
    Setting not valid with user keywords

Small typo should provide recommendation
    [Documentation]    FAIL
    ...    Non-existing setting 'Doc Umentation'. Did you mean:
    ...    ${SPACE*4}Documentation
    Small typo should provide recommendation

*** Keywords ***
Normal name
    No Operation

user_keyword nameS _are_not_ FORmatted
    No Operation

Documentation
    [Documentation]    Documentation for this user keyword
    No Operation

Documentation in multiple columns
    [Documentation]    Documentation    for this user keyword          in multiple columns
    No Operation

Documentation in multiple rows
    [DOCUMENTATION]    ${1}st line is shortdoc.
    ...
    ...                Documentation for this user keyword
    ...                in\nmultiple\nlines
    No Operation

Short doc consists of first logical, not physical, line
    [Documentation]    ${1}st logical line is shortdoc.
    ...                It can be split to
    ...                multiple
    ...                physical
    ...                lines.
    ...
    ...                Documentation after first empty row is considered
    ...                documentation body and it is not included in short doc.
    No Operation

Documentation with variables
    [Documentation]    Variables work in documentation since Robot ${VERSION}.
    No Operation

Documentation with non-existing variables
    [Documentation]    Starting from RF ${2}.1 ${NONEX} variables are left unchanged.
    No Operation

Documentation with unclosed variables
    [Documentation]    Not ${closed
    No Operation

Documentation with escaping
    [Documentation]    \${XXX} - c:\\temp - \ - \\
    No Operation

Arguments
    [Arguments]    ${arg1}    ${arg2}=default    @{varargs}    &{kwargs}
    Log Many    ${arg1}    ${arg2}    @{varargs}    &{kwargs}

Teardown
    No Operation
    [Teardown]    Log    Keyword teardown

Teardown with variables
    ${log} =    Set Variable    Log
    [Teardown]    ${log}    ${log}ged using variables

Teardown with escaping
    No Operation
    [Teardown]    Log    \${notvar} is not a variable

Return
    [Return]    Return value

Return using variables
    ${ret} =    Set Variable    Return value ${2}
    [Return]    ${ret}

Return multiple
    [ARGUMENTS]    ${arg1}    ${arg2}
    ${result} =    Evaluate    ${arg1} + ${arg2}
    [RETURN]    ${arg1}    +    ${arg2}    =    ${result}

Return with escaping
    [Return]    \${XXX}    c:\\temp    \    \\

Timeout
    [Timeout]    123 seconds
    No Operation

Timeout with variables
    [TIMEout]    ${VERSION} DAYS
    No Operation

Invalid timeout
    [Timeout]    invalid
    No Operation

Multiple settings
    [Arguments]    ${name}
    [Documentation]    Documentation for a user keyword
    [Timeout]    0.1 hours
    [Teardown]    Log    Teardown ${name}
    RETURN    Hello ${name}!!

Invalid
    [Invalid Setting]    This is invalid
    No Operation

Setting not valid with user keywords
    [Metadata]    Not valid.
    [Template]    Not valid.
    No Operation

Small typo should provide recommendation
    [Doc Umentation]
    No Operation

Invalid empty line continuation in arguments should throw an error
    [Arguments]
    ...
    No Operation

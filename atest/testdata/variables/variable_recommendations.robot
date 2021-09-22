*** Settings ***
Library         OperatingSystem
Variables       variable_recommendation_vars.py

*** Variables ***
${STRING}         Hello world!
${INTEGER}        ${42}
@{ONE ITEM}       Hello again?
@{LIST}           Hello    again    ?
${S LIST}         Not recommended as list
&{D LIST}         Recommended=as list
${SIMILAR VAR 1}
${SIMILAR VAR 2}
${SIMILAR VAR 3}
${Cäersŵs}
${INDENT}         ${SPACE * 4}
&{DICTIONARY}     key=value
${S DICTIONARY}   Not recommended as dict
@{L DICTIONARY}   Not recommended as dict

*** Test Cases ***
Simple Typo Scalar
    [Documentation]    FAIL    Variable '${SSTRING}' not found. Did you mean:
    ...    ${INDENT}\${STRING}
    Log    ${SSTRING}

Simple Typo List - Only List-likes Are Recommended
    [Documentation]    FAIL    Variable '@{GIST}' not found. Did you mean:
    ...    ${INDENT}\@{LIST}
    ...    ${INDENT}\@{D LIST}
    Log    @{GIST}

Simple Typo Dict - Only Dicts Are Recommended
    [Documentation]    FAIL    Variable '&{BICTIONARY}' not found. Did you mean:
    ...    ${INDENT}\&{DICTIONARY}
    Log    &{BICTIONARY}

All Types Are Recommended With Scalars 1
   [Documentation]    FAIL    Variable '${MIST}' not found. Did you mean:
    ...    ${INDENT}\${LIST}
    ...    ${INDENT}\${S LIST}
    ...    ${INDENT}\${D LIST}
   Log    ${MIST}

All Types Are Recommended With Scalars 2
   [Documentation]    FAIL    Variable '${BICTIONARY}' not found. Did you mean:
   ...    ${INDENT}\${DICTIONARY}
   ...    ${INDENT}\${S DICTIONARY}
   ...    ${INDENT}\${L DICTIONARY}
   Log    ${BICTIONARY}

Access Scalar In List With Typo In Variable
    [Documentation]    FAIL    Variable '@{LLIST}' not found. Did you mean:
    ...    ${INDENT}\@{LIST}
    ...    ${INDENT}\@{D LIST}
    Log    @{LLIST}[0]

Access Scalar In List With Typo In Index
    [Documentation]    FAIL    Variable '${STRENG}' not found. Did you mean:
    ...    ${INDENT}\${STRING}
    Log    @{LIST}[${STRENG}]

Long Garbage Variable
    [Documentation]    FAIL    Variable '${dEnOKkgGlYBHwotU2bifJ56w487jD2NJxCrcM62g}' not found.
    Log    ${dEnOKkgGlYBHwotU2bifJ56w487jD2NJxCrcM62g}

Many Similar Variables
    [Documentation]    FAIL    Variable '${SIMILAR VAR}' not found. Did you mean:
    ...    ${INDENT}\${SIMILAR VAR 3}
    ...    ${INDENT}\${SIMILAR VAR 2}
    ...    ${INDENT}\${SIMILAR VAR 1}
    Log    ${SIMILAR VAR}

Misspelled Lower Case
    [Documentation]    FAIL    Variable '${sstring}' not found. Did you mean:
    ...    ${INDENT}\${STRING}
    Log    ${sstring}

Misspelled Underscore
    [Documentation]    FAIL    Variable '${_S_STRI_NG}' not found. Did you mean:
    ...    ${INDENT}\${STRING}
    Log    ${_S_STRI_NG}

Misspelled Period
    [Documentation]    FAIL    Resolving variable '${INT.EGER}' failed: Variable '${INT}' not found. Did you mean:
    ...    ${INDENT}\${INDENT}
    ...    ${INDENT}\${INTEGER}
    Log    ${INT.EGER}

Misspelled Camel Case
    [Documentation]    FAIL    Variable '@{OneeItem}' not found. Did you mean:
    ...    ${INDENT}\@{ONE ITEM}
    Log    @{OneeItem}

Misspelled Whitespace
    [Documentation]    FAIL    Variable '${S STRI NG}' not found. Did you mean:
    ...    ${INDENT}\${STRING}
    Log    ${S STRI NG}

Misspelled Env Var
    [Documentation]    FAIL    Environment variable '%{THISS_ENV_VAR_IS_SET}' not found. Did you mean:
    ...    ${INDENT}\%{THIS_ENV_VAR_IS_SET}
    Set Environment Variable  THIS_ENV_VAR_IS_SET    Env var value
    ${THISS_ENV_VAR_IS_SET} =    Set Variable    Not env var and thus not recommended
    Log    %{THISS_ENV_VAR_IS_SET}

Misspelled Env Var With Internal Variables
    [Documentation]    FAIL    Environment variable '%{YET_ANOTHER_ENV_VAR}' not found. Did you mean:
    ...    ${INDENT}\%{ANOTHER_ENV_VAR}
    Set Environment Variable    ANOTHER_ENV_VAR    ANOTHER_ENV_VAR
    Log    %{YET_%{ANOTHER_ENV_VAR}}

Misspelled List Variable With Period
    [Documentation]    FAIL    Resolving variable '${list.nnew}' failed: AttributeError: 'list' object has no attribute 'nnew'
    @{list.new} =    Create List    1    2    3
    Log    ${list.nnew}

Misspelled Extended Variable Parent
    [Documentation]    FAIL    Resolving variable '${OBJJ.name}' failed: Variable '${OBJJ}' not found. Did you mean:
    ...    ${INDENT}\${OBJ}
    Log    ${OBJJ.name}

Misspelled Extended Variable Parent As List
    [Documentation]    Extended variables are always searched as scalars.
    ...    FAIL    Resolving variable '@{OBJJ.name}' failed: Variable '${OBJJ}' not found. Did you mean:
    ...    ${INDENT}\${OBJ}
    Log    @{OBJJ.name}

Misspelled Extended Variable Child
    [Documentation]    FAIL    Resolving variable '${OBJ.nmame}' failed: AttributeError: 'ExampleObject' object has no attribute 'nmame'
    Log    ${OBJ.nmame}

Existing Non ASCII Variable Name
    [Documentation]    FAIL    Variable '${Ceärsŵs}' not found. Did you mean:
    ...    ${INDENT}\${Cäersŵs}
    Log    ${Ceärsŵs}

Non Existing Non ASCII Variable Name
    [Documentation]    FAIL    Variable '${ノಠ益ಠノ}' not found.
    Log    ${ノಠ益ಠノ}

Invalid Binary
    [Documentation]    FAIL    Variable '${0b123}' not found.
    Log    ${0b123}

Invalid Multiple Whitespace
    [Documentation]    FAIL    Resolving variable '${SPACVE * 5}' failed: Variable '${SPACVE }' not found. Did you mean:
    ...    ${INDENT}\${SPACE}
    Log    ${SPACVE * 5}

Non Existing Env Var
    [Documentation]    FAIL    Environment variable '%{THIS_ENV_VAR_DOES_NOT_EXIST}' not found.
    Log    %{THIS_ENV_VAR_DOES_NOT_EXIST}

Multiple Missing Variables
    [Documentation]    FAIL    Variable '${SSTRING}' not found. Did you mean:
    ...    ${INDENT}\${STRING}
    Log Many    ${SSTRING}    @{LLIST}

Empty Variable Name
    [Documentation]    FAIL    Variable '\${}' not found.
    Log    ${}

Environment Variable With Misspelled Internal Variables
    [Documentation]    FAIL    Variable '${nnormal_var}' not found. Did you mean:
    ...    ${INDENT}\${normal_var}
    Set Environment Variable  yet_another_env_var  THIS_ENV_VAR
    ${normal_var} =  Set Variable  IS_SET
    Log  %{%{yet_another_env_var}_${nnormal_var}}

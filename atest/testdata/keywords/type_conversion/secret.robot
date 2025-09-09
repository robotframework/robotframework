*** Settings ***
Library         Collections
Library         OperatingSystem
Library         secret.py
Variables       secret.py


*** Variables ***
${FROM_LITERAL: Secret}     this fails
${FROM_EXISTING: secret}    ${VAR_FILE}
${FROM_JOIN1: secret}       abc${VAR_FILE}efg
${FROM_JOIN2: secret}       =${VAR_FILE}=
${FROM_JOIN3: secret}       =${42}==${VAR_FILE}=
${NO_VAR: secret}           =${42}=
${FROM_ENV: SECRET}         %{SECRET=kala}
${ENV_JOIN: SECRET}         qwe%{SECRET=kala}rty
${FROM_ENV2: Secret}        %{TEMPDIR}
${FROM_ENV3: Secret}        =${84}=≈%{TEMPDIR}=
@{LIST: Secret}             ${VAR_FILE}    %{SECRET=kala}
@{LIST_LITERAL: secret}     this    fails    ${VAR_FILE}    %{SECRET=kala}
@{LIST_NORMAL}              a    b    c
@{LIST2: Secret}            @{LIST_NORMAL}
@{LIST3: Secret}            @{LIST}
&{DICT1: Secret}            var_file=${VAR_FILE}    env=%{SECRET=kala}    joined==${VAR_FILE}=
&{DICT2: secret=secret}     ${VAR_FILE}=%{SECRET=kala}
&{DICT_LITERAL: secret}     this=fails    ok=${VAR_FILE}
&{DICT_NORMAL}              a=b
&{DICT3: Secret}            &{DICT_NORMAL}
${SECRET: Secret}           ${VAR_FILE_SECRET}


*** Test Cases ***
Command line
    Should Be Equal    ${CLI.value}    From command line

Variable section: Scalar
    Should Be Equal    ${FROM_EXISTING.value}    From variable file
    Should Be Equal    ${FROM_ENV.value}         kala
    Should Be Equal    ${FROM_ENV2.value}        %{TEMPDIR}
    Should Be Equal    ${FROM_ENV3.value}        =84=≈%{TEMPDIR}=
    Should Be Equal    ${FROM_JOIN1.value}       abcFrom variable fileefg
    Should Be Equal    ${FROM_JOIN2.value}       =From variable file=
    Should Be Equal    ${FROM_JOIN3.value}       =42==From variable file=
    Should Be Equal    ${ENV_JOIN.value}         qwekalarty
    Variable Should Not Exist    ${FROM_LITERAL}
    Variable Should Not Exist    ${NO_VAR}

Variable section: List
    Should Be Equal    ${LIST[0].value}    From variable file
    Should Be Equal    ${LIST[1].value}    kala
    Variable Should Not Exist    ${LIST_LITERAL}
    Variable Should Not Exist    ${LIST2}
    Variable Should Not Exist    ${LIST3}

Variable section: Dict
    Should Be Equal    ${DICT1.var_file.value}         From variable file
    Should Be Equal    ${DICT1.env.value}              kala
    Should Be Equal    ${DICT1.joined.value}           =From variable file=
    Should Be Equal    ${{$DICT2[$VAR_FILE].value}}    kala
    Variable Should Not Exist    ${DICT_LITERAL}
    Variable Should Not Exist    ${DICT3}

VAR: Env variable
    Set Environment Variable    SECRET    VALUE1
    VAR    ${secret: secret}    %{SECRET}
    Should Be Equal    ${secret.value}    VALUE1
    VAR    ${x}    SECRET
    Set Environment Variable    SECRET    VALUE2
    VAR    ${secret: secret}    %{${x}}
    Should Be Equal    ${secret.value}    VALUE2
    VAR    ${secret: secret}    %{INLINE_SECRET=inline_secret}
    Should Be Equal    ${secret.value}    inline_secret

VAR: Join secret
    [Documentation]    FAIL
    ...    Setting variable '\${zz: secret}' failed: \
    ...    Value '111\${y}222' must have type 'Secret', got string.
    ${secret1}    Library Get Secret    111
    ${secret2}    Library Get Secret    222
    VAR    ${x: secret}    abc${secret1}
    Should Be Equal    ${x.value}    abc111
    VAR    ${y: int}    42
    VAR    ${x: secret}    ${secret2}${y}
    Should Be Equal    ${x.value}    22242
    VAR    ${x: secret}    ${secret1}${secret2}
    Should Be Equal    ${x.value}    111222
    VAR    ${x: secret}    -${secret1}--${secret2}---
    Should Be Equal    ${x.value}    -111--222---
    VAR    ${x: secret}    -${y}--${secret1}---${y}----${secret2}-----
    Should Be Equal
    ...    ${x.value}
    ...    -42--111---42----222-----
    Set Environment Variable    SECRET    VALUE10
    VAR    ${secret: secret}    11%{SECRET}22
    Should Be Equal    ${secret.value}    11VALUE1022
    VAR    ${zz: secret}    111${y}222

VAR: Broken variable
    [Documentation]    FAIL
    ...    Setting variable '\${x: Secret}' failed: Variable '${borken' was not closed properly.
    VAR    ${x: Secret}    ${borken

Create: List
    [Documentation]    FAIL
    ...    Setting variable '\@{x: secret}' failed: \
    ...    Value 'this' must have type 'Secret', got string.
    VAR    @{x: secret}    ${SECRET}    ${SECRET}
    Should Be Equal    ${x[0].value}    This is a secret used in tests
    Should Be Equal    ${x[1].value}    This is a secret used in tests
    VAR    @{x: int|secret}    22    ${SECRET}    44
    Should Be Equal    ${x[0]}    22    type=int
    Should Be Equal    ${x[1].value}    This is a secret used in tests
    Should Be Equal    ${x[2]}    44    type=int
    VAR    @{x: secret}    ${SECRET}    this    fails

Create: List by extending
    VAR    @{x: secret}    ${SECRET}    ${SECRET}
    VAR    @{x}    @{x}    @{x}
    Length Should Be    ${x}    4
    Should Be Equal    ${x[0].value}    This is a secret used in tests
    Should Be Equal    ${x[1].value}    This is a secret used in tests
    Should Be Equal    ${x[2].value}    This is a secret used in tests
    Should Be Equal    ${x[3].value}    This is a secret used in tests

Create: List of dictionaries
    VAR    &{dict1: secret}    key1=${SECRET}    key2=${SECRET}
    VAR    &{dict2: secret}    key3=${SECRET}
    VAR    @{list}    ${dict1}    ${dict2}
    Length Should Be    ${list}    2
    FOR    ${d}    IN    @{list}
        Dictionaries Should Be Equal    ${d}    ${d}
    END

Create: Dictionary
    [Documentation]    FAIL
    ...    Setting variable '\&{x: secret}' failed: \
    ...    Value 'fails' must have type 'Secret', got string.
    VAR    &{x: secret}    key=${SECRET}
    Should Be Equal    ${x.key.value}    This is a secret used in tests
    VAR    &{x: int=secret}    42=${SECRET}
    Should Be Equal    ${x[42].value}    This is a secret used in tests
    VAR    &{x: secret}    this=fails

Return value: Library keyword
    [Documentation]    FAIL
    ...    ValueError: Return value must have type 'Secret', got string.
    ${x}    Library Get Secret
    Should Be Equal    ${x.value}    This is a secret
    ${x: Secret}    Library Get Secret    value of secret here
    Should Be Equal    ${x.value}    value of secret here
    ${x: secret}    Library Not Secret

Return value: User keyword
    [Documentation]    FAIL
    ...    ValueError: Return value must have type 'Secret', got string.
    ${x}    User Keyword: Return secret
    Should Be Equal    ${x.value}    This is a secret
    ${x: Secret}    User Keyword: Return secret
    Should Be Equal    ${x.value}    This is a secret
    ${x: secret}    User Keyword: Return string

User keyword: Receive not secret
    [Documentation]    FAIL
    ...    ValueError: Argument 'secret' must have type 'Secret', got string.
    User Keyword: Receive secret    xxx    ${None}

User keyword: Receive not secret var
    [Documentation]    FAIL
    ...    ValueError: Argument 'secret' must have type 'Secret', got string.
    VAR    ${x}    y
    User Keyword: Receive secret    ${x}    ${None}

Library keyword
    User Keyword: Receive secret    ${SECRET}    This is a secret used in tests

Library keyword: not secret 1
    [Documentation]    FAIL
    ...    ValueError: Argument 'secret' must have type 'Secret', got string.
    Library receive secret    111

Library keyword: not secret 2
    [Documentation]    FAIL
    ...    ValueError: Argument 'secret' must have type 'Secret', got integer.
    Library receive secret    ${222}

Library keyword: TypedDict
    [Documentation]    FAIL
    ...    ValueError: Argument 'credential' got value \
    ...    '{'username': 'login@email.com', 'password': 'This fails'}' (DotDict) that cannot be converted to Credential: \
    ...    Item 'password' must have type 'Secret', got string.
    VAR    &{credentials}    username=login@email.com    password=${SECRET}
    ${data}    Library Receive Credential    ${credentials}
    Should Be Equal    ${data}    Username: login@email.com, Password: This is a secret used in tests
    VAR    &{credentials}    username=login@email.com    password=This fails
    Library Receive Credential    ${credentials}

Library keyword: List of secrets
    VAR    @{secrets: secret}    ${SECRET}    ${SECRET}
    ${data}    Library List Of Secrets    ${secrets}
    Should Be Equal    ${data}    This is a secret used in tests, This is a secret used in tests


*** Keywords ***
User Keyword: Receive secret
    [Arguments]    ${secret: secret}    ${expected: str}
    Should Be Equal    ${secret.value}    ${expected}

User Keyword: Return secret
    ${secret}    Library Get Secret
    RETURN    ${secret}

User Keyword: Return string
    RETURN    This is a string

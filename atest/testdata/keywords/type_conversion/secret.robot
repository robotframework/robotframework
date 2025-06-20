*** Settings ***
Library         Collections
Library         OperatingSystem
Library         secret.py
Variables       secret.py


*** Variables ***
${FROM_LITERAL: Secret}     this fails
${FROM_EXISTING: secret}    ${VAR_FILE}
${FROM_JOIN: secret}        abc${VAR_FILE}efg
${FROM_ENV: SECRET}         %{SECRET=kala}
${ENV_JOIN: SECRET}         qwe%{SECRET=kala}rty
@{LIST: Secret}             ${VAR_FILE}    %{SECRET=kala}
@{LIST_LITERAL: secret}     this    fails    ${VAR_FILE}    %{SECRET=kala}
&{DICT1: Secret}            var_file=${VAR_FILE}    env=%{SECRET=kala}
&{DICT2: secret=secret}     ${VAR_FILE}=%{SECRET=kala}
&{DICT_LITERAL: secret}     this=fails    ok=${VAR_FILE}


*** Test Cases ***
Command line
    Should Be Equal    ${CLI.value}    From command line

Variable section: Scalar
    Should Be Equal    ${FROM_EXISTING.value}    From variable file
    Should Be Equal    ${FROM_ENV.value}    kala
    Should Be Equal    ${FROM_JOIN.value}    abcFrom variable fileefg
    Should Be Equal    ${ENV_JOIN.value}    qwekalarty
    Variable Should Not Exist    ${FROM_LITERAL}

Variable section: List
    Should Be Equal    ${LIST[0].value}    From variable file
    Should Be Equal    ${LIST[1].value}    kala
    Variable Should Not Exist    ${LIST_LITERAL}

Variable section: Dict
    Should Be Equal    ${DICT1.var_file.value}    From variable file
    Should Be Equal    ${DICT1.env.value}    kala
    Should Be Equal    ${{$DICT2[$VAR_FILE].value}}    kala
    Variable Should Not Exist    ${DICT_LITERAL}

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
    ...    Value '111${y}222' has types: 'string', 'integer', 'string', \
    ...    but does not have 'Secret' type.
    ${secret}    Library Get Secret
    VAR    ${x: secret}    111${secret}
    Should Be Equal    ${x.value}    111This is a secret
    VAR    ${y: int}    42
    VAR    ${x: secret}    ${secret}${y}
    Should Be Equal    ${x.value}    This is a secret42
    VAR    ${x: secret}    ${secret}${secret}
    Should Be Equal    ${x.value}    This is a secretThis is a secret
    VAR    ${x: secret}    111${secret}222${secret}333
    Should Be Equal    ${x.value}    111This is a secret222This is a secret333
    VAR    ${x: secret}    abc${y}123${secret}xyz${y}098${secret}foobar
    Should Be Equal
    ...    ${x.value}
    ...    abc42123This is a secretxyz42098This is a secretfoobar
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
    ${secret}    Library Get Secret
    VAR    @{x: secret}    ${secret}    ${secret}
    Should Be Equal    ${x[0].value}    This is a secret
    Should Be Equal    ${x[1].value}    This is a secret
    VAR    @{x: int|secret}    22    ${secret}    44
    Should Be Equal    ${x[0]}    22    type=int
    Should Be Equal    ${x[1].value}    This is a secret
    Should Be Equal    ${x[2]}    44    type=int
    VAR    @{x: secret}    ${secret}    this    fails

Create: List by extending
    ${secret}    Library Get Secret
    VAR    @{x: secret}    ${secret}    ${secret}
    VAR    @{x}    @{x}    @{x}
    Length Should Be    ${x}    4
    Should Be Equal    ${x[0].value}    This is a secret
    Should Be Equal    ${x[1].value}    This is a secret
    Should Be Equal    ${x[2].value}    This is a secret
    Should Be Equal    ${x[3].value}    This is a secret

Create: List of dictionaries
    ${secret}    Library Get Secret
    VAR    &{dict1: secret}    key1=${secret}    key2=${secret}
    VAR    &{dict2: secret}    key3=${secret}
    VAR    @{list}    ${dict1}    ${dict2}
    Length Should Be    ${list}    2
    FOR    ${d}    IN    @{list}
        Dictionaries Should Be Equal    ${d}    ${d}
    END

Create: Dictionary
    [Documentation]    FAIL
    ...    Setting variable '\&{x: secret}' failed: \
    ...    Value 'fails' must have type 'Secret', got string.
    ${secret}    Library Get Secret
    VAR    &{x: secret}    key=${secret}
    Should Be Equal    ${x.key.value}    This is a secret
    VAR    &{x: int=secret}    42=${secret}
    Should Be Equal    ${x[42].value}    This is a secret
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
    ${secret: secret}    Library Get Secret
    User Keyword: Receive secret    ${secret}    This is a secret

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
    ${secret: secret}    Library Get Secret
    VAR    &{credentials}    username=login@email.com    password=${secret}
    ${data}    Library Receive Credential    ${credentials}
    Should Be Equal    ${data}    Username: login@email.com, Password: This is a secret
    VAR    &{credentials}    username=login@email.com    password=This fails
    Library Receive Credential    ${credentials}

Library keyword: List of secrets
    ${secret: secret}    Library Get Secret
    VAR    @{secrets: secret}    ${secret}    ${secret}
    ${data}    Library List Of Secrets    ${secrets}
    Should Be Equal    ${data}    This is a secret, This is a secret


*** Keywords ***
User Keyword: Receive secret
    [Arguments]    ${secret: secret}    ${expected: str}
    Should Be Equal    ${secret.value}    ${expected}

User Keyword: Return secret
    ${secret}    Library Get Secret
    RETURN    ${secret}

User Keyword: Return string
    RETURN    This is a string

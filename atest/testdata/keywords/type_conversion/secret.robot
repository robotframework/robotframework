*** Settings ***
Library          Collections
Library          OperatingSystem
Library          secret.py
Variables        secret.py

*** Variables ***
${SECRET: Secret}           ${VAR_FILE}
${ENV1: SECRET}             %{TEMPDIR}
${ENV2: secret}             %{NONEX=kala}
${LITERAL: Secret}          this fails
${BAD: Secret}              ${666}
${JOIN1: Secret}            =${SECRET}=
${JOIN2: Secret}            =\=\\=%{TEMPDIR}=\\=\=\${ESCAPED}=
${JOIN3: Secret}            =${3}=${SECRET}=
${JOIN4: Secret}            this fails ${2}!
@{LIST1: Secret}            ${SECRET}    %{TEMPDIR}    =${SECRET}=
@{LIST2: Secret}            ${SECRET}    @{LIST1}    @{EMPTY}
@{LIST3: Secret}            this    ${SECRET}    fails
@{LIST4: Secret}            ${SECRET}    @{{["this", "fails"]}}    ${SECRET}
&{DICT1: Secret}            var=${SECRET}    env=%{TEMPDIR}    join==${SECRET}=
&{DICT2: Secret}            ${2}=${SECRET}    &{DICT1}    &{EMPTY}
&{DICT3: Secret=Secret}     %{TEMPDIR}=${SECRET}    \=%{TEMPDIR}\===${SECRET}=
&{DICT4: Secret}            ok=${SECRET}    this=fails
&{DICT5: str=Secret}        ok=${SECRET}    &{DICT1}    &{{{"this": "fails"}}}

*** Test Cases ***
Command line
    Should Be Equal    ${CLI.value}    From command line

Variable section: Based on existing variable
    Should Be Equal    ${SECRET.value}    Secret value

Variable section: Based on environment variable
    Should Be Equal    ${ENV1.value}    %{TEMPDIR}
    Should Be Equal    ${ENV2.value}    kala

Variable section: Joined
    Should Be Equal    ${JOIN1.value}    =Secret value=
    Should Be Equal    ${JOIN2.value}    ==\\=%{TEMPDIR}=\\==\${ESCAPED}=
    Should Be Equal    ${JOIN3.value}    =3=Secret value=

Variable section: Scalar fail
    Variable Should Not Exist    ${LITERAL}
    Variable Should Not Exist    ${JOIN4}

Variable section: List
    Should Be Equal
    ...    ${{[item.value for item in $LIST1]}}
    ...    ["Secret value", r"%{TEMPDIR}", "=Secret value="]
    ...    type=list
    Should Be Equal
    ...    ${{[item.value for item in $LIST2]}}
    ...    ["Secret value", "Secret value", r"%{TEMPDIR}", "=Secret value="]
    ...    type=list

Variable section: List fail
    Variable Should Not Exist    ${LIST3}
    Variable Should Not Exist    ${LIST4}

Variable section: Dict
    Should Be Equal
    ...    ${{{k: v.value for k, v in $DICT1.items()}}}
    ...    {"var": "Secret value", "env": r"%{TEMPDIR}", "join": "=Secret value="}
    ...    type=dict
    Should Be Equal
    ...    ${{{k: v.value for k, v in $DICT2.items()}}}
    ...    {2: "Secret value", "var": "Secret value", "env": r"%{TEMPDIR}", "join": "=Secret value="}
    ...    type=dict
    Should Be Equal
    ...    ${{{k.value: v.value for k, v in $DICT3.items()}}}
    ...    {r"%{TEMPDIR}": "Secret value", r"=%{TEMPDIR}=": "=Secret value="}
    ...    type=dict

Variable section: Dict fail
    Variable Should Not Exist    ${DICT4}
    Variable Should Not Exist    ${DICT5}

VAR: Based on existing variable
    [Documentation]    FAIL
    ...    Setting variable '${bad: secret}' failed: \
    ...    Value must have type 'Secret', got integer.
    VAR    ${x: Secret}    ${SECRET}
    Should Be Equal    ${x.value}    Secret value
    VAR    ${x: Secret | int}    ${SECRET}
    Should Be Equal    ${x.value}    Secret value
    VAR    ${x: Secret | int}    ${42}
    Should Be Equal    ${x}    ${42}
    VAR    ${bad: secret}    ${666}

VAR: Based on environment variable
    [Documentation]    FAIL
    ...    Setting variable '\${nonex: Secret}' failed: \
    ...    Environment variable '\%{NONEX}' not found.
    Set Environment Variable    SECRET    VALUE1
    VAR    ${secret: secret}    %{SECRET}
    Should Be Equal    ${secret.value}    VALUE1
    Set Environment Variable    SECRET    VALUE2
    VAR    ${secret: secret}    %{${{'SECRET'}}}
    Should Be Equal    ${secret.value}    VALUE2
    VAR    ${secret: secret}    %{NONEX=default}
    Should Be Equal    ${secret.value}    default
    VAR    ${secret: secret}    %{=not so secret}
    Should Be Equal    ${secret.value}    not so secret
    VAR    ${not_secret: Secret | str}    %{TEMPDIR}
    Should Be Equal    ${not_secret}    %{TEMPDIR}
    VAR    ${nonex: Secret}    %{NONEX}

VAR: Joined
    [Documentation]    FAIL
    ...    Setting variable '\${zz: secret}' failed: \
    ...    Value must have type 'Secret', got string.
    ${secret1} =    Library Get Secret    111
    ${secret2} =    Library Get Secret    222
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

VAR: List
    [Documentation]    FAIL
    ...    Setting variable '@{x: Secret | int}' failed: \
    ...    Value '[Secret(value=<secret>), 'this', 'fails']' (list) \
    ...    cannot be converted to list[Secret | int]: \
    ...    Item '1' got value 'this' that cannot be converted to Secret or integer.
    VAR    @{x: secret}    ${SECRET}    %{TEMPDIR}    \${escaped} with ${SECRET}
    Should Be Equal
    ...    ${{[item.value for item in $x]}}
    ...    ["Secret value", r"%{TEMPDIR}", "\${escaped} with Secret value"]
    ...    type=list
    VAR    @{y: Secret}    @{x}    @{EMPTY}    ${SECRET}
    Should Be Equal
    ...    ${{[item.value for item in $y]}}
    ...    ["Secret value", r"%{TEMPDIR}", "\${escaped} with Secret value", "Secret value"]
    ...    type=list
    VAR    @{z: int|secret}    22    ${SECRET}    44
    Should Be Equal    ${z}    ${{[22, $SECRET, 44]}}
    VAR    @{x: Secret | int}    ${SECRET}    this    fails

Create: Dict 1
    [Documentation]    FAIL
    ...    Setting variable '\&{x: secret}' failed: \
    ...    Value '{'this': 'fails'}' (DotDict) cannot be converted to dict[Any, secret]: \
    ...    Item 'this' must have type 'Secret', got string.
    VAR    &{x: Secret}    var=${SECRET}    end=%{TEMPDIR}    join==${SECRET}=
    Should Be Equal
    ...    ${{{k: v.value for k, v in $DICT1.items()}}}
    ...    {"var": "Secret value", "env": r"%{TEMPDIR}", "join": "=Secret value="}
    ...    type=dict
    VAR    &{x: Secret=int}    ${SECRET}=42
    Should Be Equal    ${x}    ${{{$SECRET: 42}}}
    VAR    &{x: secret}    this=fails

Create: Dict 2
    [Documentation]    FAIL
    ...    Setting variable '\&{x: Secret=int}' failed: \
    ...    Value '{Secret(value=<secret>): '42', 'bad': '666'}' (DotDict) \
    ...    cannot be converted to dict[Secret, int]: \
    ...    Key must have type 'Secret', got string.
    VAR    &{x: Secret=int}    ${SECRET}=42    bad=666

Return value: Library keyword
    [Documentation]    FAIL
    ...    ValueError: Return value must have type 'Secret', got string.
    ${x} =    Library Get Secret
    Should Be Equal    ${x.value}    This is a secret
    ${x: Secret} =    Library Get Secret    value of secret here
    Should Be Equal    ${x.value}    value of secret here
    ${x: secret} =    Library Not Secret

Return value: User keyword
    [Documentation]    FAIL
    ...    ValueError: Return value must have type 'Secret', got string.
    ${x} =    User Keyword: Return secret
    Should Be Equal    ${x.value}    This is a secret
    ${x: Secret} =    User Keyword: Return secret
    Should Be Equal    ${x.value}    This is a secret
    ${x: secret} =    User Keyword: Return string

User keyword: Receive not secret
    [Documentation]    FAIL
    ...    ValueError: Argument 'secret' must have type 'Secret', got string.
    User Keyword: Receive secret    xxx

User keyword: Receive not secret var
    [Documentation]    FAIL
    ...    ValueError: Argument 'secret' must have type 'Secret', got integer.
    User Keyword: Receive secret    ${666}

Library keyword
    User Keyword: Receive secret    ${SECRET}    Secret value

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
    ...    '{'username': 'login@email.com', 'password': 'This fails'}' (DotDict) \
    ...    that cannot be converted to Credential: \
    ...    Item 'password' must have type 'Secret', got string.
    VAR    &{credentials}    username=login@email.com    password=${SECRET}
    ${data} =    Library Receive Credential    ${credentials}
    Should Be Equal    ${data}    Username: login@email.com, Password: Secret value
    VAR    &{credentials}    username=login@email.com    password=This fails
    Library Receive Credential    ${credentials}

Library keyword: List of secrets
    VAR    @{secrets: secret}    ${SECRET}    ${SECRET}
    ${data} =    Library List Of Secrets    ${secrets}
    Should Be Equal    ${data}    Secret value, Secret value

*** Keywords ***
User Keyword: Receive secret
    [Arguments]    ${secret: secret}    ${expected: str}=not set
    Should Be Equal    ${secret.value}    ${expected}

User Keyword: Return secret
    ${secret}    Library Get Secret
    RETURN    ${secret}

User Keyword: Return string
    RETURN    This is a string

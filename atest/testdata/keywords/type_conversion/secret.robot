*** Settings ***
Library         OperatingSystem
Library         secret.py
Variables       secret.py


*** Variables ***
${FROM_LITERAL: Secret}     this fails
${FROM_EXISTING: secret}    ${VAR_FILE}
${FROM_ENV: SECRET}         %{SECRET=kala}
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
    VAR    ${x}    SECRET
    Set Environment Variable    SECRET    VALUE1
    VAR    ${secret: secret}    %{SECRET}
    Should Be Equal    ${secret.value}    VALUE1
    Set Environment Variable    SECRET    VALUE2
    VAR    ${secret: secret}    %{${x}}
    Should Be Equal    ${secret.value}    VALUE2

Create: List
    [Documentation]    FAIL
    ...    REGEXP:Setting variable '\@{x: secret}' failed: \
    ...    Value '\\[<robot\\.utils\\.secret\\.Secret object at \\S+>, 'this', 'fails'\\]' \\(list\\) cannot be converted to list\\[secret\\]: \
    ...    Item '1' must have type 'Secret', got string\\.
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

Create: Dictionary
    [Documentation]    FAIL
    ...    Setting variable '\&{x: secret}' failed: \
    ...    Value '{'this': 'fails'}' (DotDict) cannot be converted to dict[Any, secret]: \
    ...    Item 'this' must have type 'Secret', got string.
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


*** Keywords ***
User Keyword: Receive secret
    [Arguments]    ${secret: secret}    ${expected: str}
    Should Be Equal    ${secret.value}    ${expected}

User Keyword: Return secret
    ${secret}    Library Get Secret
    RETURN    ${secret}

User Keyword: Return string
    RETURN    This is a string

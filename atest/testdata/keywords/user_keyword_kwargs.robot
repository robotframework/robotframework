*** Settings ***
Library           Collections

*** Variables ***
${VAR}            value
&{DICT}           key=value    arg=${2}    preserve=order    ==

*** Test Cases ***
Kwargs only
    ${ret} =    Kwargs only
    Should Be Equal    ${ret}    ${EMPTY}
    ${ret} =    Kwargs only    key=value
    Should Be Equal    ${ret}    key: value
    ${ret} =    Kwargs only    a=1    ${VAR}=${2}    .=3    preserve=order    =
    Should Be Equal    ${ret}    a: 1, value: 2, .: 3, preserve: order, :${SPACE}
    ${ret} =    Kwargs only    esc\=key=value    \${path}=c:\\temp    bs\\=\\
    Should Be Equal    ${ret}    esc=key: value, \${path}: c:\\temp, bs\\: \\
    ${ret} =    Kwargs only    nön-äscii=\u2603
    Should Be Equal    ${ret}    nön-äscii: \u2603

Positional and kwargs
    ${ret} =    Positional and kwargs    pos1    pos2
    Should Be Equal    ${ret}    pos1, pos2
    ${ret} =    Positional and kwargs    p1    p2    x=1    a=2    preserve=order
    Should Be Equal    ${ret}    p1, p2, x: 1, a: 2, preserve: order
    ${ret} =    Positional and kwargs    x=1    a=2    arg2=named2    pre=serve
    ...    arg1=named1    z=${42}
    Should Be Equal    ${ret}    named1, named2, x: 1, a: 2, pre: serve, z: 42

Positional with defaults and kwargs
    ${ret} =    Positional with defaults and kwargs
    Should Be Equal    ${ret}    default
    ${ret} =    Positional with defaults and kwargs    pos
    Should Be Equal    ${ret}    pos
    ${ret} =    Positional with defaults and kwargs    a=1    b=2
    Should Be Equal    ${ret}    default, a: 1, b: 2
    ${ret} =    Positional with defaults and kwargs    pos    a=1    b=2
    Should Be Equal    ${ret}    pos, a: 1, b: 2
    ${ret} =    Positional with defaults and kwargs    a=1    b=2    pre=serve
    ...    arg=named    a=overrides    ${VAR}=${42}
    Should Be Equal    ${ret}    named, a: overrides, b: 2, pre: serve, value: 42

Varags and kwargs
    ${ret} =    Varags and kwargs
    Should Be Equal    ${ret}    ${EMPTY}
    ${ret} =    Varags and kwargs    arg    key=value
    Should Be Equal    ${ret}    arg, key: value
    ${ret} =    Varags and kwargs    arg    ${VAR}    key=value    ${VAR}=${42}
    Should Be Equal    ${ret}    arg, value, key: value, value: 42

Positional, varargs and kwargs
    ${ret} =    Positional, varargs and kwargs    pos
    Should Be Equal    ${ret}    pos
    ${ret} =    Positional, varargs and kwargs    pos    key=value
    Should Be Equal    ${ret}    pos, key: value
    ${ret} =    Positional, varargs and kwargs    1    2    ${3}    4    5
    ...    a=1    b=2    preserve=order    c=3    ${VAR}=${42}
    Should Be Equal    ${ret}    1, 2, 3, 4, 5, a: 1, b: 2, preserve: order, c: 3, value: 42

Positional with defaults, varargs and kwargs
    ${ret} =    Positional with defaults, varargs and kwargs
    Should Be Equal    ${ret}    "", 42
    ${ret} =    Positional with defaults, varargs and kwargs    key=value    arg2=given
    Should Be Equal    ${ret}    "", given, key: value
    ${ret} =    Positional with defaults, varargs and kwargs    k1=v1    k2=v2
    ...    arg1=not used    k3=v3    arg2=a2    k4=v4    arg1=override    k1=override
    Should Be Equal    ${ret}    override, a2, k1: override, k2: v2, k3: v3, k4: v4
    ${ret} =    Positional with defaults, varargs and kwargs    1    2    ${3}
    ...    a=1    b=2    preserve=order    c=3    ${VAR}=${42}
    Should Be Equal    ${ret}    1, 2, 3, a: 1, b: 2, preserve: order, c: 3, value: 42

Kwargs are ordered
    &{kwargs} =    Kwargs are ordered    first=1    override=this    third=3
    ...    4=${4}    =5    override=again    this\=is\=key=6    \==7    8=8
    ...    9=9    10=${0 + 10}    nön-äscii=11    12=12    override=2
    ...    lucky?=13    2nd last=14    last=15
    ${values} =    Catenate    @{kwargs.values()}
    Should Be Equal    ${values}    1 2 3 4 5 6 7 8 9 10 11 12 13 14 15

Kwargs are dot-accessible
    ${kwargs} =    Kwargs are dot-accessible    key=value    second=${2}
    Should Be Equal    ${kwargs.key}    value
    Should Be Equal    ${kwargs.second}    ${2}

Too few positional arguments
    [Documentation]    FAIL Keyword 'Positional and kwargs' expected 2 non-named arguments, got 1.
    Positional and kwargs    one positional is not enough

Too many positional arguments
    [Documentation]    FAIL Keyword 'Kwargs only' expected 0 non-named arguments, got 3.
    Kwargs only    positional    not    accepted

Positional after kwargs
    [Documentation]    FAIL Keyword 'Varags and kwargs' got positional argument after named arguments.
    Varags and kwargs    key=value    positional

Non-String Keys
    [Documentation]    FAIL Argument names must be strings.
    Kwargs only    ${42}=not allowed

Calling using dict variables
    ${ret} =    Kwargs only    &{EMPTY}
    Should Be Equal    ${ret}   ${EMPTY}
    ${ret} =    Kwargs only    &{DICT}
    Should Be Equal    ${ret}   key: value, arg: 2, preserve: order, : =
    ${ret} =    Positional with defaults and kwargs    &{DICT}
    Should Be Equal    ${ret}   2, key: value, preserve: order, : =
    ${ret} =    Positional, varargs and kwargs    key=not used    &{DICT}    new=item
    Should Be Equal    ${ret}   2, key: value, preserve: order, : =, new: item
    ${ret} =    Positional, varargs and kwargs    key=not used    &{DICT}    arg=used
    ...    new=item    &{EMPTY}    preserve=order still
    Should Be Equal    ${ret}    used, key: value, preserve: order still, : =, new: item

Caller does not see modifications to kwargs
    &{d1} =    Create Dictionary    key=value1
    &{d2} =    Create Dictionary    key=value2
    Mutate Dictionaries    ${d1}    &{d2}
    Should Be Equal    ${d1.new}    item1
    Variable Should Not Exist    ${d2.new}

Invalid arguments spec: Positional after kwargs
    [Documentation]    FAIL Invalid argument specification: Only last argument can be kwargs.
    Positional after kwargs

Invalid arguments spec: Varargs after kwargs
    [Documentation]    FAIL Invalid argument specification: Only last argument can be kwargs.
    Varargs after kwargs

*** Keywords ***
Kwargs only
    [Arguments]    &{kwargs}
    Run Keyword And Return    Varags and kwargs    &{kwargs}

Positional and kwargs
    [Arguments]    ${arg1}    ${arg2}    &{kwargs}
    Run Keyword And Return    Varags and kwargs    ${arg1}    ${arg2}    &{kwargs}

Positional with defaults and kwargs
    [Arguments]    ${arg}=default    &{kwargs}
    Run Keyword And Return    Varags and kwargs    ${arg}    &{kwargs}

Varags and kwargs
    [Arguments]    @{varargs}    &{kwargs}
    @{items} =    Create List    @{varargs}
    FOR    ${key}    IN    @{kwargs}
        ${value} =    Get From Dictionary    ${kwargs}    ${key}
        Append To List    ${items}    ${key}: ${value}
    END
    ${result} =    Catenate    SEPARATOR=,${SPACE}    @{items}
    RETURN    ${result}

Positional, varargs and kwargs
    [Arguments]    ${arg}    @{varargs}    &{kwargs}
    Run Keyword And Return    Varags and kwargs    ${arg}    @{varargs}    &{kwargs}

Positional with defaults, varargs and kwargs
    [Arguments]    ${arg1}="${EMPTY}"    ${arg2}=${40 + 2}    @{varargs}    &{kwargs}
    Run Keyword And Return    Varags and kwargs    ${arg1}    ${arg2}    @{varargs}    &{kwargs}

Kwargs are ordered
    [Arguments]    &{kwargs}
    ${values} =    Catenate    @{kwargs.values()}
    Should Be Equal    ${values}    1 2 3 4 5 6 7 8 9 10 11 12 13 14 15
    RETURN    &{kwargs}

Kwargs are dot-accessible
    [Arguments]    &{kwargs}
    Should Be Equal    ${kwargs.key}    value
    Should Be Equal    ${kwargs.second}    ${2}
    RETURN    &{kwargs}

Mutate Dictionaries
    [Arguments]    ${dict1}    &{dict2}
    Should Be Equal    ${dict1.key}    value1
    Should Be Equal    ${dict2.key}    value2
    ${dict1.new} =    Set Variable    item1
    ${dict2.new} =    Set Variable    item2
    Should Be Equal    ${dict1.new}    item1
    Should Be Equal    ${dict2.new}    item2

Positional after kwargs
    [Arguments]    &{kwargs}    ${positional}
    No Operation

Varargs after kwargs
    [Arguments]    &{kwargs}    @{varargs}
    No Operation

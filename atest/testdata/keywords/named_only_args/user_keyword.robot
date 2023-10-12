*** Variables ***
${VAR}         value

*** Test Cases ***
Mandatory arguments
    ${result} =    Kw Only Arg    kwo=value
    Should Be Equal    ${result}    value
    ${result} =    Many Kw Only Args    first=${1}    third=${3}    second=${2}
    Should Be Equal    ${result}    ${6}

Default values
    ${result} =    Kw Only Arg With Default
    Should Be Equal    ${result}    default-another
    ${result} =    Kw Only Arg With Default    kwo=value
    Should Be Equal    ${result}    value-another
    ${result} =    Kw Only Arg With Default    another=${2}    kwo=1
    Should Be Equal    ${result}    1-2

Mandatory Can Be After Default
    ${result} =    Mandatory After Defaults    mandatory=yyy
    Should Be Equal    ${result}    xxx-yyy-zzz
    ${result} =    Mandatory After Defaults    default2=3    mandatory=2    default1=1
    Should Be Equal    ${result}    1-2-3

Variable in default value
    ${result} =    Kw Only Arg With Variable In Default
    Should Be Equal    ${result}    1-value-1
    ${result} =    Kw Only Arg With Variable In Default    ko1=xxx
    Should Be Equal    ${result}    xxx-value-xxx
    ${result} =    Kw Only Arg With Variable In Default    ko3=bar    ko2=foo
    Should Be Equal    ${result}    1-foo-bar
    ${result} =    Kw Only Arg With Variable In Default    ko1=a    ko3=c    ko2=b
    Should Be Equal    ${result}    a-b-c

Last given value has precedence
    ${result} =    Kw Only Arg    kwo=ignored    kwo=ignored2    kwo=used
    Should Be Equal    ${result}    used

Missing value 1
    [Documentation]    FAIL Keyword 'Kw Only Arg' missing named-only argument 'kwo'.
    Kw Only Arg

Missing value 2
    [Documentation]    FAIL Keyword 'Mandatory After Defaults' missing named-only argument 'mandatory'.
    Mandatory After Defaults    default2=this is not enough

Missing multiple values
    [Documentation]    FAIL Keyword 'Many Kw Only Args' missing named-only arguments 'first' and 'third'.
    Many Kw Only Args    second=xxx

Unexpected keyword argument
    [Documentation]    FAIL Keyword 'Kw Only Arg' got unexpected named argument 'invalid'.
    Kw Only Arg    kwo=value    invalid=ooops

Multiple unexpected keyword argument
    [Documentation]    FAIL Keyword 'Kw Only Arg' got unexpected named arguments 'invalid' and 'ooops'.
    Kw Only Arg    kwo=value    invalid=ooops    ooops=invalid

Unexpected positional argument 1
    [Documentation]    FAIL Keyword 'Kw Only Arg' expected 0 non-named arguments, got 1.
    Kw Only Arg    ooops

Unexpected positional argument 2
    [Documentation]    FAIL Keyword 'Kw Only Arg' expected 0 non-named arguments, got 1.
    Kw Only Arg    ooops    kwo=value

With varargs
    ${result} =    Kw Only Arg With Varargs    kwo=xxx
    Should Be Equal    ${result}    xxx
    ${result} =    Kw Only Arg With Varargs    1    2    3    kwo=4
    Should Be Equal    ${result}    1-2-3-4

With other arguments
    ${result} =    All Arg Types    pos    kwo_req=kwo
    Should Be Equal    ${result}    pos-pd-kwo-kd
    ${result} =    All Arg Types    p1    p2    kwo_def=k2    kwo_req=k1
    Should Be Equal    ${result}    p1-p2-k1-k2
    ${result} =    All Arg Types    p1    p2    p3    p4    k3=3    kwo_def=k2    kwo_req=k1    k4=4
    Should Be Equal    ${result}    p1-p2-p3-p4-k1-k2-k3=3-k4=4
    ${result} =    All Arg Types    k3=!    kwo_def=k2    k4=!!!    pos_req=p1    pos_def=p2    kwo_req=k1
    Should Be Equal    ${result}    p1-p2-k1-k2-k3=!-k4=!!!

Argument name as variable
    ${name} =    Set Variable    kwo
    ${result} =    Kw Only Arg    ${name}=value
    Should Be Equal    ${result}    value
    ${result} =    Kw Only Arg    k${name[1]}o=xxx
    Should Be Equal    ${result}    xxx
    ${result} =    Kw Only Arg With Default    another=${name}    ${name}=${EMPTY}
    Should Be Equal    ${result}    -kwo

Argument name as non-existing variable
    [Documentation]    FAIL Variable '${i do not exist}' not found.
    Kw Only Arg    ${i do not exist}=value

With positional argument containing equal sign
    ${result} =    Kw Only Arg With Varargs    One more time    a=1    <=    2    kwo=No escaping needed!
    Should Be Equal    ${result}    One more time-a=1-<=-2-No escaping needed!

*** Keywords ***
Kw Only Arg
    [Arguments]    @{}    ${kwo}
    RETURN    ${kwo}

Many Kw Only Args
    [Arguments]    @{}    ${first}    ${second}    ${third}
    ${result} =    Evaluate    $first + $second + $third
    RETURN    ${result}

Kw Only Arg With Default
    [Arguments]    @{}    ${kwo}=default    ${another}=another
    RETURN    ${kwo}-${another}

Mandatory After Defaults
    [Arguments]    @{}    ${default1}=xxx    ${mandatory}    ${default2}=zzz
    RETURN    ${default1}-${mandatory}-${default2}

Kw Only Arg With Variable In Default
    [Arguments]    @{}    ${ko1}=${1}    ${ko2}=${VAR}    ${ko3}=${ko1}
    RETURN    ${ko1}-${ko2}-${ko3}

Kw Only Arg With Varargs
    [Arguments]    @{varargs}    ${kwo}
    ${result} =    Catenate    SEPARATOR=-    @{varargs}    ${kwo}
    RETURN    ${result}

All Arg Types
    [Arguments]    ${pos_req}    ${pos_def}=pd    @{varargs}
    ...            ${kwo_req}    ${kwo_def}=kd    &{kwargs}
    @{kwargs} =    Evaluate    ['%s=%s' % item for item in $kwargs.items()]
    ${result} =    Catenate    SEPARATOR=-
    ...    ${pos_req}    ${pos_def}    @{varargs}
    ...    ${kwo_req}    ${kwo_def}    @{kwargs}
    RETURN    ${result}

*** Settings ***
Library           DynamicKwOnlyArgs.py
Library           DynamicKwOnlyArgsWithoutKwargs.py

*** Test Cases ***
Mandatory arguments
    Kw Only Arg              kwo=value
    Args Should Have Been    kwo=value
    Many Kw Only Args        first=${1}    third=${3}    second=${2}
    Args Should Have Been    first=${1}    third=${3}    second=${2}

Default values
    Kw Only Arg With Default
    Args Should Have Been
    Kw Only Arg With Default    kwo=value
    Args Should Have Been       kwo=value
    Kw Only Arg With Default    another=${2}    kwo=1
    Args Should Have Been       another=${2}    kwo=1

Mandatory Can Be After Default
    Mandatory After Defaults    mandatory=yyy
    Args Should Have Been       mandatory=yyy
    Mandatory After Defaults    default2=3      mandatory=2      default1=1
    Args Should Have Been       default1=1      mandatory=2      default2=3

Last given value has precedence
    Kw Only Arg    kwo=ignored    kwo=ignored2    kwo=used
    Args Should Have Been    kwo=used

Missing value
    [Documentation]    FAIL Keyword 'DynamicKwOnlyArgs.Kw Only Arg' missing named-only argument 'kwo'.
    Kw Only Arg

Missing multiple values
    [Documentation]    FAIL Keyword 'DynamicKwOnlyArgs.Many Kw Only Args' missing named-only arguments 'first' and 'third'.
    Many Kw Only Args    second=xxx

Unexpected keyword argumemt
    [Documentation]    FAIL Keyword 'DynamicKwOnlyArgs.Kw Only Arg' got unexpected named argument 'invalid'.
    Kw Only Arg    kwo=value    invalid=ooops

Multiple unexpected keyword argumemt
    [Documentation]    FAIL Keyword 'DynamicKwOnlyArgs.Kw Only Arg' got unexpected named arguments 'invalid' and 'ooops'.
    Kw Only Arg    kwo=value    invalid=ooops    ooops=invalid

Unexpected positional argument 1
    [Documentation]    FAIL Keyword 'DynamicKwOnlyArgs.Kw Only Arg' expected 0 non-named arguments, got 1.
    Kw Only Arg    ooops

Unexpected positional argument 2
    [Documentation]    FAIL Keyword 'DynamicKwOnlyArgs.Kw Only Arg' expected 0 non-named arguments, got 1.
    Kw Only Arg    ooops    kwo=value

With varargs
    Kw Only Arg With Varargs    kwo=xxx
    Args Should Have Been       kwo=xxx
    Kw Only Arg With Varargs    1    2    3    kwo=4
    Args Should Have Been       1    2    3    kwo=4

With other arguments
    All Arg Types            pos       kwo_req=kwo
    Args Should Have Been    pos       kwo_req=kwo
    All Arg Types            p1        p2             kwo_def=k2    kwo_req=k1
    Args Should Have Been    p1        p2             kwo_def=k2    kwo_req=k1
    All Arg Types            p1        p2             p3            p4    k3=3    kwo_def=k2    kwo_req=k1    k4=4
    Args Should Have Been    p1        p2             p3            p4    k3=3    kwo_def=k2    kwo_req=k1    k4=4
    All Arg Types            k4=!!!    kwo_def=k2     k3=!          pos_req=p1    pos_def=p2    kwo_req=k1
    Args Should Have Been    k4=!!!    kwo_def=k2     k3=!          pos_req=p1    pos_def=p2    kwo_req=k1

Using kw-only arguments is not possible if 'run_keyword' accepts no kwargs
    [Documentation]    FAIL No keyword with name 'No kwargs' found.
    No kwargs    kwo=value

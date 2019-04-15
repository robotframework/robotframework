*** Settings ***
Library           KwOnlyArgs.py

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

Annotation
    ${result} =    Kw Only Arg With Annotation    kwo=Annotations are OK!
    Should Be Equal    ${result}    Annotations are OK!

Annotation and default value
    ${result} =    Kw Only Arg With Annotation And Default
    Should Be Equal    ${result}    default
    ${result} =    Kw Only Arg With Annotation And Default    kwo=value
    Should Be Equal    ${result}    value

Last given value has precedence
    ${result} =    Kw Only Arg    kwo=ignored    kwo=ignored2    kwo=used
    Should Be Equal    ${result}    used

Missing value
    [Documentation]    FAIL Keyword 'KwOnlyArgs.Kw Only Arg' missing named-only argument 'kwo'.
    Kw Only Arg

Missing multiple values
    [Documentation]    FAIL Keyword 'KwOnlyArgs.Many Kw Only Args' missing named-only arguments 'first' and 'third'.
    Many Kw Only Args    second=xxx

Unexpected keyword argument
    [Documentation]    FAIL Keyword 'KwOnlyArgs.Kw Only Arg' got unexpected named argument 'invalid'.
    Kw Only Arg    kwo=value    invalid=ooops

Multiple unexpected keyword argument
    [Documentation]    FAIL Keyword 'KwOnlyArgs.Kw Only Arg' got unexpected named arguments 'invalid' and 'ooops'.
    Kw Only Arg    kwo=value    invalid=ooops    ooops=invalid

Multiple unexpected keyword argument with inequality
    [Documentation]    FAIL Keyword 'KwOnlyArgs.Kw Only Arg' got unexpected named arguments '<' and 'ooops'.
    Kw Only Arg    kwo=value    <=ooops    ooops=invalid

Multiple unexpected keyword argument with escaped inequality
    [Documentation]    FAIL Keyword 'KwOnlyArgs.Kw Only Arg' got positional argument after named arguments.
    Kw Only Arg    kwo=value    <\=ooops    ooops=invalid

Unexpected positional argument 1
    [Documentation]    FAIL Keyword 'KwOnlyArgs.Kw Only Arg' expected 0 non-named arguments, got 1.
    Kw Only Arg    ooops

Unexpected positional argument 2
    [Documentation]    FAIL Keyword 'KwOnlyArgs.Kw Only Arg' expected 0 non-named arguments, got 1.
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
    ${result} =    All Arg Types    k4=!!!    kwo_def=k2    k3=!    pos_req=p1    pos_def=p2    kwo_req=k1
    Should Be Equal    ${result}    p1-p2-k1-k2-k3=!-k4=!!!

With only one named argument
    Kw Two Args With Varargs    First arg    Second arg    Maybe a third    kwo=Actually, correct!

With only one named argument but we have a escaped egal
    Kw Two Args With Varargs    Let's try this again    1    <\=    2    kwo=Correct again!

With only one named argument but we have a no escaped egal
    Kw Two Args With Varargs    One more time    1    <=    2    kwo=This part fails

With only one named argument but we have two no escaped egals
    Kw Two Args With Varargs    One more time    a=1    <=    2    kwo=This part fails

With two named arguments but with a error
    [Documentation]  FAIL    Keyword 'KwOnlyArgs.Kw Two Args With Varargs' got positional argument after named arguments.
    Kw Two Args With Varargs    One more time    another=1    2      <=     kwo=This part fails

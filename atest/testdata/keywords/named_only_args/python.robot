*** Settings ***
Library           KWOArgs.py

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
    [Documentation]    FAIL Keyword 'KWOArgs.Kw Only Arg' missing named-only argument 'kwo'.
    Kw Only Arg

Missing multiple values
    [Documentation]    FAIL Keyword 'KWOArgs.Many Kw Only Args' missing named-only arguments 'first' and 'third'.
    Many Kw Only Args    second=xxx

Unexpected keyword argumemt
    [Documentation]    FAIL Keyword 'KWOArgs.Kw Only Arg' got unexpected named argument 'invalid'.
    Kw Only Arg    kwo=value    invalid=ooops

Multiple unexpected keyword argumemt
    [Documentation]    FAIL Keyword 'KWOArgs.Kw Only Arg' got unexpected named arguments 'invalid' and 'ooops'.
    Kw Only Arg    kwo=value    invalid=ooops    ooops=invalid

Unexpected positional argument
    [Documentation]    FAIL Keyword 'KWOArgs.Kw Only Arg' expected 0 non-keyword arguments, got 1.
    Kw Only Arg    ooops    kwo=value

*** Settings ***
Library           PositionalOnly.py
Force Tags        require-py3.8

*** Test Cases ***
Normal usage
    ${result} =    One argument    arg
    Should be equal    ${result}    ARG
    ${result} =    Three arguments    1    2    3
    Should be equal    ${result}    1-2-3
    ${result} =    With normal    foo    bar
    Should be equal    ${result}    foo-bar
    ${result} =    With normal    foo    normal=bar
    Should be equal    ${result}    foo-bar

Named syntax is not used
    ${result} =    One argument    what=ever
    Should be equal    ${result}    WHAT=EVER
    ${result} =    One argument    arg=arg
    Should be equal    ${result}    ARG=ARG
    ${result} =    With normal    posonly=foo    bar
    Should be equal    ${result}    posonly=foo-bar
    ${result} =    With normal    posonly=foo    normal=bar
    Should be equal    ${result}    posonly=foo-bar

Default values
    ${result} =    Defaults    first
    Should be equal    ${result}    first-default
    ${result} =    Defaults    first    second
    Should be equal    ${result}    first-second

Type conversion
    ${result} =    Types    1    2.5
    Should be equal    ${result}    ${3.5}

Too few arguments 1
    [Documentation]    FAIL Keyword 'PositionalOnly.Three Arguments' expected 3 arguments, got 2.
    Three arguments    1    2

Too few arguments 2
    [Documentation]    FAIL Keyword 'PositionalOnly.Defaults' expected 1 to 2 arguments, got 0.
    Defaults

Too many arguments 1
    [Documentation]    FAIL Keyword 'PositionalOnly.One Argument' expected 1 argument, got 3.
    One argument    too    many    args

Too many arguments 2
    [Documentation]    FAIL Keyword 'PositionalOnly.With Normal' expected 2 arguments, got 3.
    With normal    too    many    args

Named argument syntax doesn't work after valid named arguments
    [Documentation]    FAIL Keyword 'PositionalOnly.With Normal' does not accept argument 'posonly' as named argument.
    With normal    normal=would work    posonly=fails

Name can be used with kwargs
    ${result} =    Kwargs    posonly    x=1    y=2
    Should be equal    ${result}    posonly, x: 1, y: 2

Mandatory positional-only missing with kwargs
    [Documentation]    FAIL Keyword 'PositionalOnly.Kwargs' expected 1 non-named argument, got 0.
    Kwargs    x=1

*** Settings ***
Library           PositionalOnly.py

*** Test Cases ***
Normal usage
    ${result} =    One argument    arg
    Should be equal    ${result}    ARG
    ${result} =    Three arguments    1    2    3
    Should be equal    ${result}    1, 2, 3
    ${result} =    With normal    foo    bar
    Should be equal    ${result}    foo, bar
    ${result} =    With normal    foo    normal=bar
    Should be equal    ${result}    foo, bar

Default values
    ${result} =    Defaults    first
    Should be equal    ${result}    first, default
    ${result} =    Defaults    first    second
    Should be equal    ${result}    first, second

Positional only value can contain '=' without it being considered named argument
    ${result} =    One argument    what=ever
    Should be equal    ${result}    WHAT=EVER
    ${result} =    One argument    arg=arg
    Should be equal    ${result}    ARG=ARG
    ${result} =    With normal    posonly=foo    bar
    Should be equal    ${result}    posonly=foo, bar
    ${result} =    With normal    posonly=foo    normal=bar
    Should be equal    ${result}    posonly=foo, bar
    ${result} =    With normal    named=positional value for 'posonly'    posonly=positional value for 'named'
    Should be equal    ${result}    named=positional value for 'posonly', posonly=positional value for 'named'
    ${result} =    With kwargs    x=y    name=value
    Should be equal    ${result}    x=y, name: value
    ${result} =    With kwargs    x=y    x=z
    Should be equal    ${result}    x=y, x: z

Name of positional only argument can be used with kwargs
    ${result} =    With kwargs    posonly    x=1    y=2
    Should be equal    ${result}    posonly, x: 1, y: 2

Type conversion
    ${result} =    Types    1    2.5
    Should be equal    ${result}    ${3.5}

Too few arguments 1
    [Documentation]    FAIL Keyword 'PositionalOnly.Three Arguments' expected 3 arguments, got 2.
    Three arguments    1    2

Too few arguments 2
    [Documentation]    FAIL Keyword 'PositionalOnly.Defaults' expected 1 to 2 arguments, got 0.
    Defaults

Too few arguments 3
    [Documentation]    FAIL Keyword 'PositionalOnly.With Kwargs' expected 1 non-named argument, got 0.
    With kwargs

Too many arguments 1
    [Documentation]    FAIL Keyword 'PositionalOnly.One Argument' expected 1 argument, got 3.
    One argument    too    many    args

Too many arguments 2
    [Documentation]    FAIL Keyword 'PositionalOnly.Defaults' expected 1 to 2 arguments, got 3.
    Defaults    too    many    args

Too many arguments 3
    [Documentation]    FAIL Keyword 'PositionalOnly.With Kwargs' expected 1 non-named argument, got 2.
    With kwargs    one    two

*** Settings ***
Library           String

*** Variables ***
@{EXCLUDES}       a    an    the    to    is
@{EXCLUDES 2}     (a|b|c)[.,]?

*** Test Cases ***
Convert To Upper Case
    [Template]    Test upper case
    ${EMPTY}       ${EMPTY}
    abcd           ABCD
    1234           1234
    a1b2C3d4e      A1B2C3D4E
    Hello world    HELLO WORLD
    ööääåå         ÖÖÄÄÅÅ

Convert To Lower Case
    [Template]    Test lower case
    ${EMPTY}       ${EMPTY}
    ABCD           abcd
    1234           1234
    A1B2c3D4E      a1b2c3d4e
    Hello world    hello world
    ÖÖÄÄÅÅ         ööääåå

Convert To Title Case
    [Template]    Test title case
    ${EMPTY}                              ${EMPTY}
    abcd                                  Abcd
    äiti                                  Äiti
    XML                                   XML
    jUnit                                 jUnit
    3.14                                  3.14
    ----                                  ----
    3tm                                   3Tm
    \u2603                                \u2603
    \u2603snowman                         \u2603Snowman
    hello world                           Hello World
    don't title t                         Don't Title T
    'do' title "these"                    'Do' Title "These"
    i don't have iPhone x11 & it's OK     I Don't Have iPhone X11 & It's OK
    they're bill's friends from the UK    They're Bill's Friends From The UK
    ääliö älä lyö, ööliä läikkyy!         Ääliö Älä Lyö, Ööliä Läikkyy!

Convert To Titlecase preserves whitespace
    [Template]    Test title case
    foo${SPACE*100}bar    Foo${SPACE*100}Bar
    foo\tbar              Foo\tBar
    foo\nbar              Foo\nBar
    foo\rbar              Foo\rBar
    foo\r\nbar            Foo\r\nBar
    foo\xa0bar            Foo\xa0Bar
    foo\u3000bar          Foo\u3000Bar
    \nfoo\tbar\r          \nFoo\tBar\r

Convert To Title Case with excludes
    [Template]    Test title case
    this is an example    This is an Example    is, an
    this is an example    This is an Example    ${EXCLUDES}
    äiti ei ole iso       äiti Ei Ole Iso       exclude=äiti
    Isä on iso            Isä on Iso            exclude=äiti,isä,on
    they're bill's friends from the UK
    ...                   They're Bill's Friends From the UK
    ...                                         exclude=${EXCLUDES}
    this is none          This Is none          exclude=none

Convert To Title Case with regexp excludes
    [Template]    Test title case
    a, b, and c.          A, B, And C.          exclude=a, b, c    # doesn't work!
    a, b, and c.          a, b, And c.          exclude=(a|b|c).
    a, b, and c.          a, b, And c.          exclude=${EXCLUDES2}
    full match only!      Full Match Only!      exclude=.
    full match only!      full Match Only!      exclude=....

Convert To Title Case does not work with bytes
    [Documentation]    FAIL    TypeError: This keyword works only with strings.
    Convert To Title Case    ${{b'xxx'}}

*** Keywords ***
Test upper case
    [Arguments]    ${string}    ${expected}
    ${result} =    Convert To Upper Case    ${string}
    Should be Equal    ${result}    ${expected}

Test lower case
    [Arguments]    ${string}    ${expected}
    ${result} =    Convert To Lower Case    ${string}
    Should be Equal    ${result}    ${expected}

Test title case
    [Arguments]    ${string}    ${expected}    @{args}    &{kwargs}
    ${result} =    Convert To Title Case    ${string}    @{args}    &{kwargs}
    Should be Equal    ${result}    ${expected}

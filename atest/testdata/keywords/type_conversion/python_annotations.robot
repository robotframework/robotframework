*** Settings ***
Library           PythonAnnotations.py

*** Variables ***
@{LIST}           foo         bar
&{DICT}           foo=${1}    bar=${2}

*** Test Cases ***
Integer
    Integer       42                      ${42}
    Integer       -1                      ${-1}

Float as integer
    Integer       1.0                     ${1.0}
    Integer       1.5                     ${1.5}

Invalid integer
    [Template]    Conversion Should Fail
    Integer       foobar

Float
    Float         1.5                     ${1.5}
    Float         -1                      ${-1.0}

Invalid float
    [Template]    Conversion Should Fail
    Float         foobar

Decimal
    Decimal       3.14                    Decimal('3.14')
    Decimal       -1                      Decimal('-1')
    Decimal       1e6                     Decimal('1000000')

Invalid decimal
    [Template]    Conversion Should Fail
    Decimal       foobar

Boolean
    Boolean       True                    ${True}
    Boolean       false                   ${False}
    Boolean       no                      ${False}
    Boolean       none                    ${None}

Invalid boolean is accepted as-is
    Boolean       FooBar                  "FooBar"
    Boolean       ${EMPTY}                ""

List
    List          []                      []
    List          ['foo', 'bar']          ${LIST}
    List          [1, 2, 3.14, -42]       [1, 2, 3.14, -42]

Invalid list
    [Template]    Conversion Should Fail
    List          [1, ooops]
    List          {}
    List          ooops

Tuple
    Tuple         ()                      ()
    Tuple         ('foo', "bar")          tuple(${LIST})
    Tuple         (1, 2, 3.14, -42)       (1, 2, 3.14, -42)

Invalid tuple
    [Template]    Conversion Should Fail
    Tuple         (1, ooops)
    Tuple         {}
    Tuple         ooops

Dictionary
    Dictionary    {}                      {}
    Dictionary    {'foo': 1, "bar": 2}    dict(${DICT})
    Dictionary    {1: 2, 3.14: -42}       {1: 2, 3.14: -42}

Invalid dictionary
    [Template]    Conversion Should Fail
    Dictionary    {1: ooops}
    Dictionary    []
    Dictionary    ooops

Set
    Set           set()                   set()
    Set           {'foo', 'bar'}          {'foo', 'bar'}
    Set           {1, 2, 3.14, -42}       {1, 2, 3.14, -42}

Invalid set
    [Template]    Conversion Should Fail
    Set           {1, ooops}
    Set           {}
    Set           ooops

Enum
    Enum          BAR                     Foo.BAR

Invalid Enum
    [Template]    Conversion Should Fail
    Enum          foobar                  type=Foo

Bytes
    Bytes         foo                     b'foo'
    Bytes         \x00\x01\xFF\u00FF      b'\\x00\\x01\\xFF\\xFF'
    Bytes         Hyvä esimerkki!         b'Hyv\\xE4 esimerkki!'

Invalid bytes
    [Template]    Conversion Should Fail
    Bytes         \u0100

Unknown types are not converted
    Unknown       foo                     "foo"
    Unknown       1                       "1"
    Unknown       true                    "true"
    Unknown       None                    "None"
    Unknown       none                    "none"

Non-strings are not converted
    [Template]    Non-string is not converted
    Integer
    Float
    Boolean
    Decimal
    List
    Tuple
    Dictionary
    Set
    Enum
    Bytes

String None is converted to None object
    [Template]    String None is converted to None object
    Integer
    Float
    Boolean
    Decimal
    List
    Tuple
    Dictionary
    Set
    Enum
    Bytes

*** Keywords ***
Conversion Should Fail
    [Arguments]    ${kw}    ${arg}    ${type}=${kw.lower()}
    ${error} =    Run Keyword And Expect Error    *    ${kw}    ${arg}
    Should Be Equal    ${error}
    ...    ValueError: Argument 'argument' cannot be converted to ${type}, got '${arg}'.

Non-string is not converted
    [Arguments]    ${kw}
    Run Keyword    ${kw}    ${1}       ${1}
    Run Keyword    ${kw}    ${1.5}     ${1.5}
    Run Keyword    ${kw}    ${True}    ${True}
    Run Keyword    ${kw}    ${None}    ${None}
    Run Keyword    ${kw}    ${LIST}    ${LIST}
    Run Keyword    ${kw}    ${DICT}    ${DICT}

String None is converted to None object
    [Arguments]    ${kw}
    Run Keyword    ${kw}    None       ${None}
    Run Keyword    ${kw}    NONE       ${None}
    Run Keyword    ${kw}    none       ${None}

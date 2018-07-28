*** Settings ***
Library           PythonAnnotations.py

*** Variables ***
@{LIST}           foo      bar
@{EMPTY LIST}
@{NUMBER LIST}    ${1}     ${2}    ${3.14}    ${-42}
&{DICT}           foo=1    bar=2

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

Boolean
    Boolean       True                    ${True}
    Boolean       false                   ${False}

Invalid boolean is accepted as-is
    Boolean       foobar                  foobar

List
    List          []                      ${EMPTY LIST}
    List          ['foo', 'bar']          ${LIST}
    List          [1, 2, 3.14, -42]       ${NUMBER LIST}

Invalid list
    [Template]    Conversion Should Fail
    List          [1, ooops]
    List          {}
    List          ooops

Tuple
    Tuple         ()                      tuple(${EMPTY LIST})
    Tuple         ('foo', 'bar')          tuple(${LIST})
    Tuple         (1, 2, 3.14, -42)       tuple(${NUMBER LIST})

Invalid tuple
    [Template]    Conversion Should Fail
    Tuple         (1, ooops)
    Tuple         {}
    Tuple         ooops

Dictionary
    Dictionary    {}                      {}
    Dictionary    {'foo': 1, 'bar': 2}    {'foo': 1, 'bar': 2}
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
    Enum          BAR                 Foo.BAR

Invalid Enum
    [Template]    Conversion Should Fail
    Enum          foobar    type=Foo

Non-strings are not converted
    [Template]    Non-string is not converted
    Integer
    Float
    Boolean
    List
    Tuple
    Dictionary
    Set

String None is converted to None object
    [Template]    String None is converted to None object
    Integer
    Float
    Boolean
    List
    Tuple
    Dictionary
    Set

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

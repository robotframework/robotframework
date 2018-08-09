*** Settings ***
Library                       AnnotationsWithTyping.py

*** Test Cases ***
Dict
    Dict                      {}                          {}
    Dict                      {'foo': 1, "bar": 2}        {'foo': 1, "bar": 2}
    Dict                      {1: 2, 3.14: -42}           {1: 2, 3.14: -42}

Dict with params
    Dict with params          {}                          {}
    Dict with params          {'foo': 1, "bar": 2}        {'foo': 1, "bar": 2}
    Dict with params          {1: 2, 3.14: -42}           {1: 2, 3.14: -42}

Invalid dictionary
    [Template]                Conversion Should Fail
    Dict                      {1: ooops}                  type=dictionary
    Dict                      []                          type=dictionary
    Dict with params          ooops                       type=dictionary

List
    List                      []                          []
    List                      ['foo', 'bar']              ['foo', 'bar']
    List                      [1, 2, 3.14, -42]           [1, 2, 3.14, -42]

List with params
    List with params          []                          []
    List with params          ['foo', 'bar']              ['foo', 'bar']
    List with params          [1, 2, 3.14, -42]           [1, 2, 3.14, -42]

Invalid list
    [Template]                Conversion Should Fail
    List                      [1, oops]
    List                      ()
    List with params          ooops                       type=list

Set
    Set                       set()                       set()
    Set                       {'foo', 'bar'}              {'foo', 'bar'}
    Set                       {1, 2, 3.14, -42}           {1, 2, 3.14, -42}

Set with params
    Set with params           set()                       set()
    Set with params           {'foo', 'bar'}              {'foo', 'bar'}
    Set with params           {1, 2, 3.14, -42}           {1, 2, 3.14, -42}

Invalid Set
    [Template]                Conversion Should Fail
    Set                       {1, ooops}
    Set                       {}
    Set                       ooops

Iterable
    Iterable                  ['list', 'is', 'ok']        ['list', 'is', 'ok']
    Iterable                  ('tuple',)                  ('tuple',)
    Iterable                  set()                       set()
    Iterable                  {'dict': 'accepted'}        {'dict': 'accepted'}

Iterable with params
    Iterable with params      ['list', 'is', 'ok']        ['list', 'is', 'ok']
    Iterable with params      ('tuple',)                  ('tuple',)
    Iterable with params      set()                       set()
    Iterable with params      {'dict': 'accepted'}        {'dict': 'accepted'}

Invalid iterable
    [Template]                Conversion Should Fail
    Iterable                  foobar

Mapping
    Mapping                   {}                          {}
    Mapping                   {'foo': 1, "bar": 2}        {'foo': 1, "bar": 2}
    Mapping                   {1: 2, 3.14: -42}           {1: 2, 3.14: -42}

Mapping with params
    Mapping with params       {}                          {}
    Mapping with params       {'foo': 1, "bar": 2}        {'foo': 1, "bar": 2}
    Mapping with params       {1: 2, 3.14: -42}           {1: 2, 3.14: -42}

Invalid mapping
    [Template]                Conversion Should Fail
    Mapping                   {1: ooops}
    Mapping                   []
    Mapping with params       ooops                       type=mapping

*** Keywords ***
Conversion Should Fail
    [Arguments]    ${kw}    ${arg}    ${type}=${kw.lower()}
    ${error} =    Run Keyword And Expect Error    *    ${kw}    ${arg}
    Should Be Equal    ${error}
    ...    ValueError: Argument 'argument' cannot be converted to ${type}, got '${arg}'.

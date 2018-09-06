*** Settings ***
Library                       AnnotationsWithTyping.py
Resource                      conversion.resource

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
    Dict                      {1: ooops}                  type=dictionary      error=Invalid expression.
    Dict                      []                          type=dictionary      error=Value is list, not dict.
    Dict with params          ooops                       type=dictionary      error=Invalid expression.

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
    List                      [1, oops]                                        error=Invalid expression.
    List                      ()                                               error=Value is tuple, not list.
    List with params          ooops                       type=list            error=Invalid expression.

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
    Set                       {1, ooops}                                       error=Invalid expression.
    Set                       {}                                               error=Value is dictionary, not set.
    Set                       ooops                                            error=Invalid expression.

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
    Iterable                  foobar                                           error=Failed to convert to list, tuple, set or dictionary.

Sequence
    Sequence                  ['list', 'is', 'ok']        ['list', 'is', 'ok']
    Sequence                  ('tuple',)                  ('tuple',)

Sequence with params
    Sequence with params      ['list', 'is', 'ok']        ['list', 'is', 'ok']
    Sequence with params      ('tuple',)                  ('tuple',)

Invalid sequence
    [Template]                Conversion Should Fail
    Sequence                  foobar                                           error=Failed to convert to list or tuple.
    Sequence                  {'a': 1, 'b': 2}                                 error=Failed to convert to list or tuple.
    Sequence with params      {1, 2, 3}                   type=sequence        error=Failed to convert to list or tuple.

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
    Mapping                   {1: ooops}                  type=dictionary      error=Invalid expression.
    Mapping                   []                          type=dictionary      error=Value is list, not dict.
    Mapping with params       ooops                       type=dictionary      error=Invalid expression.

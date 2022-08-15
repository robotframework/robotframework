*** Settings ***
Library                       AnnotationsWithTyping.py
Resource                      conversion.resource

*** Test Cases ***
List
    List                      []                          []
    List                      ['foo', 'bar']              ['foo', 'bar']
    List                      [1, 2, 3.14, -42]           [1, 2, 3.14, -42]

List with params
    List with ints            []                          []
    @{numbers}=               Create list  1  ${2}  3  -42
    List with ints            ${numbers}                  [1, 2, 3, -42]
    List with ints            [1, ${2}, 1313, -42]        [1, 2, 1313, -42]
    List with enums           ['foo', 'bar']              [MyEnum.foo, MyEnum.bar]

Invalid list
    [Template]                Conversion Should Fail
    List                      [1, oops]                                        error=Invalid expression.
    List                      ()                                               error=Value is tuple, not list.
    List with ints            ooops                       type=List[int]       error=Invalid expression.
    List with ints            [1, ${2}, 3.14, -42]        type=List[int]       error=Argument 'List[2]' got value '3.14' (float) that cannot be converted to integer: Conversion would lose precision.

Sequence
    Sequence                  []                          []
    Sequence                  ['foo', 'bar']              ['foo', 'bar']
    Mutable sequence          [1, 2, 3.14, -42]           [1, 2, 3.14, -42]

Sequence with params
    Sequence with params      []                          []
    Sequence with params      ['foo', 'bar']              ['foo', 'bar']
    Mutable sequence with params
    ...                       [1, 2, 3.14, -42]           [1, 2, 3.14, -42]

Invalid Sequence
    [Template]                Conversion Should Fail
    Sequence                  [1, oops]                   type=list            error=Invalid expression.
    Mutable sequence          ()                          type=list            error=Value is tuple, not list.
    Sequence with params      ooops                       type=List[bool]      error=Invalid expression.

Dict
    Dict                      {}                          {}
    Dict                      {'foo': 1, "bar": 2}        {'foo': 1, "bar": 2}
    Dict                      {1: 2, 3.14: -42}           {1: 2, 3.14: -42}

Dict with params
    Dict with str_int         {}                             {}
    Dict with str_int         {'foo': 1, "bar": 2}           {'foo': 1, "bar": 2}
    Dict with str_int         {1: 2, 3.14: -42}              {'1': 2, '3.14': -42}
    Dict with enums           {'foo': True, 'bar': 'False'}  {MyEnum.foo: True, MyEnum.bar: False}

TypedDict
    TypedDict                 {'x': 1}                    {'x': 1}
    # Following would fail if we'd validate TypedDict and didn't only convert to dict.
    TypedDict                 {}                          {}
    TypedDict                 {'foo': 1, "bar": 2}        {'foo': 1, "bar": 2}
    TypedDict                 {1: 2, 3.14: -42}           {1: 2, 3.14: -42}

Invalid dictionary
    [Template]                Conversion Should Fail
    Dict                      {1: ooops}                  type=dictionary      error=Invalid expression.
    Dict                      []                          type=dictionary      error=Value is list, not dict.
    Dict with str_int         ooops                       type=Dict[str:int]   error=Invalid expression.

Mapping
    Mapping                   {}                          {}
    Mapping                   {'foo': 1, "bar": 2}        {'foo': 1, "bar": 2}
    Mutable mapping           {1: 2, 3.14: -42}           {1: 2, 3.14: -42}

Mapping with params
    Mapping with params       {}                          {}
    Mapping with params       {'foo': 1, "bar": 2}        {'foo': 1, "bar": 2}
    Mutable mapping with params
    ...                       {1: 2, 3.14: -42}           {1: 2, 3.14: -42}

Invalid mapping
    [Template]                Conversion Should Fail
    Mapping                   {1: ooops}                  type=dictionary      error=Invalid expression.
    Mutable mapping           []                          type=dictionary      error=Value is list, not dict.
    Mapping with params       ooops                       type=Dict[bool:int]  error=Invalid expression.

Set
    Set                       set()                       set()
    Set                       {'foo', 'bar'}              {'foo', 'bar'}
    Mutable set               {1, 2, 3.14, -42}           {1, 2, 3.14, -42}

Set with params
    Set with params           set()                       set()
    Set with params           {'foo', 'bar'}              {'foo', 'bar'}
    Mutable set with params   {1, 2, 3.14, -42}           {1, 2, 3.14, -42}

Invalid Set
    [Template]                Conversion Should Fail
    Set                       {1, ooops}                                       error=Invalid expression.
    Set                       {}                                               error=Value is dictionary, not set.
    Set                       ooops                                            error=Invalid expression.

None as default
    None as default
    None as default           [1, 2, 3, 4]                [1, 2, 3, 4]

Forward references
    Forward reference         [1, 2, 3, 4]                [1, 2, 3, 4]
    Forward ref with params   [1, 2, 3, 4]                [1, 2, 3, 4]

Type hint not liking `isinstance`
    Not liking isinstance     42    42

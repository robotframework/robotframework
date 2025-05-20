Language: Finnish

*** Settings ***
Library                       AnnotationsWithTyping.py
Resource                      conversion.resource

*** Test Cases ***
List
    List                      []                          []
    List                      ['foo', 'bar']              ['foo', 'bar']
    List                      [1, 2, 3.14, -42]           [1, 2, 3.14, -42]

List with types
    List with types           []                          []
    List with types           [1, 2, 3, -42]              [1, 2, 3, -42]
    List with types           [1, '2', 3.0]               [1, 2, 3]
    List with types           ${{[1, '2', 3.0]}}          [1, 2, 3]
    ${obj} =                  Evaluate                    list(range(100))
    List with types           ${obj}                      ${obj}                       same=True

List with incompatible types
    [Template]                Conversion Should Fail
    List with types           ['foo', 'bar']              type=List[int]                error=Item '0' got value 'foo' that cannot be converted to integer.
    List with types           [0, 1, 2, 3, 4, 5, 6.1]     type=List[int]                error=Item '6' got value '6.1' (float) that cannot be converted to integer: Conversion would lose precision.
    List with types           ${{[0.0, 1.1]}}             type=List[int]                error=Item '1' got value '1.1' (float) that cannot be converted to integer: Conversion would lose precision.
    ...                       arg_type=list

Invalid list
    [Template]                Conversion Should Fail
    List                      [1, oops]                                                 error=Invalid expression.
    List                      ()                                                        error=Value is tuple, not list.
    List with types           ooops                       type=List[int]                error=Invalid expression.

Tuple
    Tuple                     ()                          ()
    Tuple                     ('foo', 'bar')              ('foo', 'bar')
    Tuple                     (1, 2, 3.14, -42)           (1, 2, 3.14, -42)

Tuple with types
    Tuple with types          ('true', 1)                 (True, 1)
    Tuple with types          ('ei', '2')                 (False, 2)    # 'ei' -> False is due to language config
    Tuple with types          ${{('no', '3')}}            (False, 3)
    ${obj} =                  Evaluate                    (True, 42)
    Tuple with types          ${obj}                      ${obj}                        same=True

Tuple with homogenous types
    Homogenous tuple          ()                          ()
    Homogenous tuple          (1,)                        (1,)
    Homogenous tuple          ('1',)                      (1,)
    Homogenous tuple          (1, '2')                    (1, 2)
    Homogenous tuple          (1, '2', 3.0, 4, 5)         (1, 2, 3, 4, 5)
    Homogenous tuple          ${{(1, '2', 3.0)}}          (1, 2, 3)
    ${obj} =                  Evaluate                    tuple(range(100))
    Homogenous tuple          ${obj}                      ${obj}                        same=True

Tuple with incompatible types
    [Template]                Conversion Should Fail
    Tuple with types          ('bad', 'values')           type=Tuple[bool, int]         error=Item '1' got value 'values' that cannot be converted to integer.
    Homogenous tuple          ('bad', 'values')           type=Tuple[int, ...]          error=Item '0' got value 'bad' that cannot be converted to integer.
    Tuple with types          ${{('bad', 'values')}}      type=Tuple[bool, int]         error=Item '1' got value 'values' that cannot be converted to integer.
    ...                       arg_type=tuple

Tuple with wrong number of values
    [Template]                Conversion Should Fail
    Tuple with types          ('false',)                  type=Tuple[bool, int]         error=Expected 2 items, got 1.
    Tuple with types          ('too', 'many', '!')        type=Tuple[bool, int]         error=Expected 2 items, got 3.

Invalid tuple
    [Template]                Conversion Should Fail
    Tuple                     (1, oops)                                                 error=Invalid expression.
    Tuple with types          []                          type=Tuple[bool, int]         error=Value is list, not tuple.
    Homogenous tuple          ooops                       type=Tuple[int, ...]          error=Invalid expression.

Sequence
    Sequence                  []                          []
    Sequence                  ['foo', 'bar']              ['foo', 'bar']
    Mutable sequence          [1, 2, 3.14, -42]           [1, 2, 3.14, -42]

Sequence with types
    Sequence with types       []                          []
    Sequence with types       [1, 2.3, '4', '5.6']        [1, 2.3, 4, 5.6]
    Mutable sequence with types
    ...                       [1, 2, 3.0, '4']            [1, 2, 3, 4]
    Sequence with types       ${{[1, 2.3, '4', '5.6']}}   [1, 2.3, 4, 5.6]

Sequence with incompatible types
    [Template]                Conversion Should Fail
    Sequence with types            [()]                   type=Sequence[int | float]    error=Item '0' got value '()' (tuple) that cannot be converted to integer or float.
    Mutable sequence with types    [1, 2, 'x', 4]         type=MutableSequence[int]     error=Item '2' got value 'x' that cannot be converted to integer.

Invalid sequence
    [Template]                Conversion Should Fail
    Sequence                  [1, oops]                   type=list                     error=Invalid expression.
    Mutable sequence          ()                          type=list                     error=Value is tuple, not list.
    Sequence with types       ooops                       type=Sequence[int | float]    error=Invalid expression.

Dict
    Dict                      {}                          {}
    Dict                      {'foo': 1, "bar": 2}        {'foo': 1, "bar": 2}
    Dict                      {1: 2, 3.14: -42}           {1: 2, 3.14: -42}

Dict with types
    Dict with types           {}                          {}
    Dict with types           {1: 1.1, 2: 2.2}            {1: 1.1, 2: 2.2}
    Dict with types           {'1': '2.2', 3.0: 4}        {1: 2.2, 3: 4.0}
    Dict with types           ${{{'1': '2', 3.0: 4}}}     {1: 2.0, 3: 4.0}
    ${obj} =                  Evaluate                    {i: float(i) for i in range(100)}
    Dict with types           ${obj}                      ${obj}                        same=True

Dict with incompatible types
    [Template]                Conversion Should Fail
    Dict with types           {1: 2, 'bad': 3}            type=Dict[int, float]         error=Key 'bad' cannot be converted to integer.
    Dict with types           {None: 0}                   type=Dict[int, float]         error=Key 'None' (None) cannot be converted to integer.
    Dict with types           {666: 'bad'}                type=Dict[int, float]         error=Item '666' got value 'bad' that cannot be converted to float.
    Dict with types           {0: None}                   type=Dict[int, float]         error=Item '0' got value 'None' (None) that cannot be converted to float.

Invalid dictionary
    [Template]                Conversion Should Fail
    Dict                      {1: ooops}                  type=dictionary               error=Invalid expression.
    Dict                      []                          type=dictionary               error=Value is list, not dict.
    Dict with types           ooops                       type=Dict[int, float]         error=Invalid expression.

Mapping
    Mapping                   {}                          {}
    Mapping                   {'foo': 1, "bar": 2}        {'foo': 1, "bar": 2}
    Mutable mapping           {1: 2, 3.14: -42}           {1: 2, 3.14: -42}

Mapping with types
    Mapping with types        {}                          {}
    Mapping with types        {1: 2, '3': 4.5}            {1: 2.0, 3: 4.5}
    Mapping with types        ${{{1: 2, '3': 4.0}}}       {1: 2.0, 3: 4.0}
    Mutable mapping with types
    ...                       {1: 2, '3': 4.5}            {1: 2.0, 3: 4.5}
    Mutable mapping with types
    ...                       ${{{1: 2, '3': 4.0}}}       {1: 2.0, 3: 4.0}

Mapping with incompatible types
    [Template]                Conversion Should Fail
    Mutable mapping with types    {'bad': 2}              type=MutableMapping[int, float]    error=Key 'bad' cannot be converted to integer.
    Mapping with types            {1: 'bad'}              type=Mapping[int, float]           error=Item '1' got value 'bad' that cannot be converted to float.

Invalid mapping
    [Template]                Conversion Should Fail
    Mapping                   {1: ooops}                  type=dictionary               error=Invalid expression.
    Mutable mapping           []                          type=dictionary               error=Value is list, not dict.
    Mapping with types        ooops                       type=Mapping[int, float]      error=Invalid expression.

TypedDict
    TypedDict                 {'x': 1, 'y': 2.0}          {'x': 1, 'y': 2}
    TypedDict                 {'x': -10_000, 'y': '2'}    {'x': -10000, 'y': 2}
    TypedDict                 ${{{'x': 1, 'y': '2'}}}     {'x': 1, 'y': 2}
    TypedDict with optional   {'x': 1, 'y': 2, 'z': 3}    {'x': 1, 'y': 2, 'z': 3}
    NotRequired               {'x': 1, 'y': 2, 'z': 3}    {'x': 1, 'y': 2, 'z': 3}
    Required                  {'x': 1, 'y': 2, 'z': 3}    {'x': 1, 'y': 2, 'z': 3}

Stringified TypedDict types
    Stringified TypedDict     {'a': 1, 'b': 2}            {'a': 1, 'b': 2}
    Stringified TypedDict     {'a': 1, 'b': 2.3}          {'a': 1, 'b': 2.3}
    Stringified TypedDict     {'a': '1', 'b': '2.3'}      {'a': 1, 'b': 2.3}

Optional TypedDict keys can be omitted (total=False)
    TypedDict with optional   {'x': 0, 'y': '0'}          {'x': 0, 'y': 0}
    TypedDict with optional   ${{{'x': 0, 'y': '0'}}}     {'x': 0, 'y': 0}

Not required TypedDict keys can be omitted (NotRequired/Required)
    NotRequired               {'x': 0, 'y': '0.1'}        {'x': 0, 'y': 0.1}
    NotRequired               ${{{'x': 0, 'y': '0'}}}     {'x': 0, 'y': 0}
    Required                  {'x': 0, 'y': '0.1'}        {'x': 0, 'y': 0.1}
    Required                  ${{{'x': 0, 'y': '0'}}}     {'x': 0, 'y': 0}

Required TypedDict keys cannot be omitted
    [Documentation]           This test would fail if using Python 3.8 without typing_extensions!
    ...                       In that case there's no information about required/optional keys.
    [Template]                Conversion Should Fail
    TypedDict                 {'x': 123}                  type=Point2D                  error=Required item 'y' missing.
    Required                  {'y': 0.1}                  type=RequiredAnnotation       error=Required item 'x' missing.
    TypedDict                 {}                          type=Point2D                  error=Required items 'x' and 'y' missing.
    TypedDict with optional   {}                          type=Point                    error=Required items 'x' and 'y' missing.

Incompatible TypedDict
    [Template]                Conversion Should Fail
    TypedDict                 {'x': 'bad'}                type=Point2D                  error=Item 'x' got value 'bad' that cannot be converted to integer.
    TypedDict                 {'bad': 1}                  type=Point2D                  error=Item 'bad' not allowed. Available items: 'x' and 'y'
    TypedDict                 {'x': 1, 'y': 2, 'z': 3}    type=Point2D                  error=Item 'z' not allowed.
    TypedDict with optional   {'x': 1, 'b': 2, 'z': 3}    type=Point                    error=Item 'b' not allowed. Available item: 'y'
    TypedDict with optional   {'b': 1, 'a': 2, 'd': 3}    type=Point                    error=Items 'a', 'b' and 'd' not allowed. Available items: 'x', 'y' and 'z'

Invalid TypedDict
    [Template]                Conversion Should Fail
    TypedDict                 {'x': oops}                 type=Point2D                  error=Invalid expression.
    TypedDict                 []                          type=Point2D                  error=Value is list, not dict.

Set
    Set                       set()                       set()
    Set                       {1, 2.0, '3'}               {1, 2.0, '3'}
    Mutable set               {1, 2, 3.14, -42}           {1, 2, 3.14, -42}

Set with types
    Set with types            set()                       set()
    Set with types            {1, 2.0, '3'}               {1, 2, 3}
    Set with types            ${{{1, 2.0, '3'}}}          {1, 2, 3}
    Mutable set with types    {1, 2, 3.14, -42}           {1, 2, 3.14, -42}
    Mutable set with types    ${{{1, 2, 3.14, -42}}}      {1, 2, 3.14, -42}
    ${obj} =                  Evaluate                    set(range(100))
    Set with types            ${obj}                      ${obj}                        same=True

Set with incompatible types
    [Template]                Conversion Should Fail
    Set with types            {1, 2.0, 'three'}           type=Set[int]                 error=Item 'three' cannot be converted to integer.
    Mutable set with types    {1, 2.0, 'three'}           type=MutableSet[float]        error=Item 'three' cannot be converted to float.

Invalid Set
    [Template]                Conversion Should Fail
    Set                       {1, ooops}                                                error=Invalid expression.
    Set                       {}                                                        error=Value is dictionary, not set.
    Set                       ooops                                                     error=Invalid expression.

Any
    Any                       hello                       'hello'
    Any                       42                          '42'
    Any                       ${42}                       42
    Any                       None                        'None'
    Any                       ${None}                     None

None as default
    None as default
    None as default           [1, 2, 3, 4]                [1, 2, 3, 4]
    None as default           NoNe                        None

None as default with Any
    [Documentation]    `a: Any = None` was same as `a: Any|None = None` prior to Python 3.11.
    ...                With unions we don't look at the default in this case and that
    ...                behavior is preserved for backwards compatiblity.
    None as default with Any
    None as default with Any    hi!                       'hi!'
    None as default with Any    ${42}                     42
    None as default with Any    None                      'None'

Forward references
    Forward reference         [1, 2, 3, 4]                [1, 2, 3, 4]
    Forward ref with types    [1, '2', 3, 4.0]            [1, 2, 3, 4]

Type hint not liking `isinstance`
    Not liking isinstance     42    42

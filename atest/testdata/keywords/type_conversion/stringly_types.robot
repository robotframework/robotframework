*** Settings ***
Library           StringlyTypes.py
Resource          conversion.resource

*** Test Cases ***
Parameterized list
    Parameterized list    []    []
    Parameterized list    [1, '2', 3]    [1, 2, 3]
    Conversion should fail
    ...    Parameterized list    [1, 'kaksi']
    ...    type=list[int]
    ...    error=Item '1' got value 'kaksi' that cannot be converted to integer.

Parameterized dict
    Parameterized dict    {}    {}
    Parameterized dict    {1: 2, 3.0: 4.5}    {1: 2.0, 3: 4.5}
    Conversion should fail
    ...    Parameterized dict    {1.1: 2}
    ...    type=dict[int, float]
    ...    error=Key '1.1' (float) cannot be converted to integer: Conversion would lose precision.

Parameterized set
    Parameterized set    set()    set()
    Parameterized set    {1, 2.3, '4.5'}    {1.0, 2.3, 4.5}
    Conversion should fail
    ...    Parameterized set    [1, 2]
    ...    type=set[float]
    ...    error=Value is list, not set.

Parameterized tuple
    Parameterized tuple    (1, 2.3, 'xxx')    (1, 2.3, 'xxx')
    Conversion should fail
    ...    Parameterized tuple    (1, 2, 'too', 'many')
    ...    type=tuple[int, float, str]
    ...    error=Expected 3 items, got 4.

Homogenous tuple
    Homogenous tuple    ()    ()
    Homogenous tuple    (1,)    (1,)
    Homogenous tuple    (1, 2.0, '3')    (1, 2, 3)
    Conversion should fail
    ...    Homogenous tuple    ('bad', 'values')
    ...    type=tuple[int, ...]
    ...    error=Item '0' got value 'bad' that cannot be converted to integer.

Literal
    Literal    one        'one'
    Literal    ${2}       2
    Literal    ${None}    None
    Literal    2          2
    Literal    ONE        'one'
    Literal    NONE       None
    Conversion should fail
    ...    Literal    bad
    ...    type='one', 2 or None

Union
    Union    1           1
    Union    1.2         1.2
    Conversion should fail
    ...    Union    bad
    ...    type=integer or float

Nested
    Nested    {}    {}
    Nested    {1: (1, 2, 3), 2.3: (2, 3.4)}    {1: (1, 2, 3), 2.3: (2, 3.4)}
    Conversion should fail
    ...    Nested    {1: (), 2: (1.1, 2.2, 3.3)}
    ...    type=dict[int | float, tuple[int, ...] | tuple[int, float]]
    ...    error=Item '2' got value '(1.1, 2.2, 3.3)' (tuple) that cannot be converted to tuple[int, ...] or tuple[int, float].

Aliases
    Aliases    [1, 2, '3']    {'1': 1.1, 2: '2.2', '': 'NONE'}

TypedDict items
    TypedDict items    {'simple': 42, 'params': [1, 2.0, '3'], 'union': 3.14}

Invalid
    [Documentation]    FAIL    No keyword with name 'Invalid' found.
    Invalid    whatever

Bad parameters
    [Documentation]    FAIL    No keyword with name 'Bad Params' found.
    Bad Params    whatever

Language: English
Language: Finnish

*** Settings ***
Library                       Literal.py
Resource                      conversion.resource

*** Test Cases ***
Integers
    [Template]    Integers
    1             1
    1.0           1
    ${2}          2
    ${3.0}        3

Invalid integers
    [Template]    Conversion Should Fail
    Integers      bad        type=1, 2 or 3
    Integers      4          type=1, 2 or 3
    Integers      ${1.1}     type=1, 2 or 3    arg_type=float

Strings
    [Template]    Strings
    a    'a'
    B    'B'

Strings are case, space, etc. insensitive
    [Template]    Strings
    A             'a'
    b             'B'
    _a_           'a'
    -b-           'B'
    \ A \         'a'

Invalid strings
    [Template]    Conversion Should Fail
    Strings       bad        type='a', 'B' or 'c'
    Strings       ${666}     type='a', 'B' or 'c'    arg_type=integer

Bytes
    [Template]    Bytes
    a             b'a'
    \xe4          b'\\xe4'
    ä             b'\\xe4'

Invalid bytes
    [Template]    Conversion Should Fail
    Bytes         c          type=b'a' or b'\\xe4'

Booleans
    [Template]    Booleans
    True          True
    true          True
    ${True}       True
    yes           True
    ON            True
    1             True
    ${1}          True

Booleans are localized
    [Template]    Booleans
    kyllä         True
    päällä        True

Invalid booleans
    [Template]    Conversion Should Fail
    Booleans      xxx        type=True
    Booleans      False      type=True
    Booleans      ${False}   type=True    arg_type=boolean

None
    [Template]    Literal.None
    None          None
    NONE          None
    ${None}       None

Invalid None
    [Template]    Conversion Should Fail
    None          xxx        type=None

Enums
    [Template]    Enums
    R             Char.R
    f             Char.F
    - r -         Char.R

Invalid enums
    [Template]    Conversion Should Fail
    Enums         W          type=R or F
    Enums         xxx        type=R or F

Int enums
    [Template]    Int enums
    one           Number.one
    __TWO__       Number.two
    ${1}          Number.one

Invalid int enums
    [Template]    Conversion Should Fail
    Int Enums     three      type=one or two
    Int Enums     ${0}       type=one or two    arg_type=integer

Multiple matches with exact match
    [Template]    Multiple Matches
    ABC           'ABC'
    abc           'abc'
    R             'R'
    ${True}       True
    True          'True'
    ${1}          1
    1             '1'

Multiple matches with not exact match
    [Template]    No Unique Match
    aBc
    r
    ${1.0}        arg_type=float

In parameters
    In params    []                           []
    In params   ['R', 'F']                   ['R', 'F']
    In params   ['R', 'r', 'f', 'R', 'F']    ['R', 'R', 'F', 'R', 'F']
    Conversion Should Fail
    ...    In params   ['R', 'F', 'W']
    ...    type=List[Literal['R', 'F']]
    ...    error=Item '2' got value 'W' that cannot be converted to 'R' or 'F'.

*** Keywords ***
No Unique Match
    [Arguments]    ${arg}    ${arg_type}=${None}
    Conversion Should Fail    Multiple Matches    ${arg}
    ...    type='ABC', 'abc', 'R', R, one, True, 1, 'True' or '1'
    ...    arg_type=${arg_type}
    ...    error=No unique match found.

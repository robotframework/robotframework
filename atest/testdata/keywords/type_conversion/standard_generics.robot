language: fi

*** Settings ***
Library           StandardGenerics.py
Resource          conversion.resource
Test Tags         require-py3.9

*** Variables ***
@{INTS}              ${1}      ${2}      ${3}
@{STRINGS}           one       2         kolme
@{MIXED}             one       ${2}      kolme
&{INT TO FLOAT}      ${1}=${2.3}
&{STR TO STR}        a=1       b=2
&{STR TO INT}        a=${1}    b=${2}

*** Test Cases ***
List
    List                             []                       []
    List                             [1, 2, 3]                [1, 2, 3]
    List                             ['1', 2.0]               [1, 2]
    List                             ${INTS}                  ${INTS}                   same=True

List with unknown
    List with unknown                []                       []
    List with unknown                [1, 2, 3]                [1, 2, 3]
    List with unknown                ${{['1', 2.0]}}          ['1', 2.0]

List in union
    List in union 1                  ['1', '2']               "['1', '2']"
    List in union 1                  ${STRINGS}               ${STRINGS}                same=True
    List in union 1                  ${MIXED}                 "${MIXED}"
    List in union 2                  ['1', '2']               "['1', '2']"
    List in union 2                  ${STRINGS}               ${STRINGS}
    List in union 2                  ${MIXED}                 ${STRINGS}

Incompatible list
    [Template]                       Conversion should fail
    List                             [1, 'bad']               type=list[int]            error=Item '1' got value 'bad' that cannot be converted to integer.
    List                             [1, 2, 3.4]              type=list[int]            error=Item '2' got value '3.4' (float) that cannot be converted to integer: Conversion would lose precision.

Tuple
    Tuple                            (1, 'true', 3.14)        (1, True, 3.14)
    Tuple                            ('1', 'ei', '3.14')      (1, False, 3.14)          # 'ei' -> False conversion is due to language config.

Tuple with unknown
    Tuple with unknown               (1, '2')                 (1, 2)
    Tuple with unknown               ${{('1', '2')}}          ('1', 2)
    Tuple with unknown               ${{['1', 2]}}            ('1', 2)

Tuple in union
    Tuple in union 1                 ('1', '2', '3')          "('1', '2', '3')"
    Tuple in union 1                 ${{tuple($STRINGS)}}     ${{tuple($STRINGS)}}
    Tuple in union 1                 ${STRINGS}               "${STRINGS}"
    Tuple in union 1                 ${MIXED}                 "${MIXED}"
    Tuple in union 2                 ('1', '2', '3')          "('1', '2', '3')"
    Tuple in union 2                 ${{tuple($STRINGS)}}     ${{tuple($STRINGS)}}
    Tuple in union 2                 ${STRINGS}               ${{tuple($STRINGS)}}
    Tuple in union 2                 ${MIXED}                 ${{tuple($STRINGS)}}

Homogenous tuple
    Homogenous Tuple                 ()                       ()
    Homogenous Tuple                 (1,)                     (1,)
    Homogenous Tuple                 (1, 2, '3', 4.0, 5)      (1, 2, 3, 4, 5)

Homogenous tuple with unknown
    Homogenous tuple with unknown    (1, '2')                 (1, '2')
    Homogenous tuple with unknown    ${{('1', '2')}}          ('1', '2')
    Homogenous tuple with unknown    ${{['1', 2]}}            ('1', 2)

Homogenous tuple in union
    Homogenous tuple in union 1      ('1', '2', '3')          "('1', '2', '3')"
    Homogenous tuple in union 1      ${{tuple($STRINGS)}}     ${{tuple($STRINGS)}}
    Homogenous tuple in union 1      ${STRINGS}               "${STRINGS}"
    Homogenous tuple in union 1      ${MIXED}                 "${MIXED}"
    Homogenous tuple in union 2      ('1', '2', '3')          "('1', '2', '3')"
    Homogenous tuple in union 2      ${{tuple($STRINGS)}}     ${{tuple($STRINGS)}}
    Homogenous tuple in union 2      ${STRINGS}               ${{tuple($STRINGS)}}
    Homogenous tuple in union 2      ${MIXED}                 ${{tuple($STRINGS)}}

Incompatible tuple
    [Template]                       Conversion should fail
    Tuple                            (1, 2, 'bad')            type=tuple[int, bool, float]    error=Item '2' got value 'bad' that cannot be converted to float.
    Homogenous Tuple                 (1, '2', 3.0, 'four')    type=tuple[int, ...]            error=Item '3' got value 'four' that cannot be converted to integer.
    Tuple                            ('too', 'few')           type=tuple[int, bool, float]    error=Expected 3 items, got 2.
    Tuple                            (1, True, 3.0, 4)        type=tuple[int, bool, float]    error=Expected 3 items, got 4.

Dict
    Dict                             {}                       {}
    Dict                             {1: 2}                   {1: 2}
    Dict                             {1: 2, '3': 4.0}         {1: 2, 3: 4}
    Dict                             ${INT TO FLOAT}          ${INT TO FLOAT}            same=True

Dict with unknown
    Dict with unknown key            {}                       {}
    Dict with unknown key            {1: 2}                   {1: 2}
    Dict with unknown key            ${{{1: 2, '3': '4'}}}    {1: 2, '3': 4}
    Dict with unknown value          {}                       {}
    Dict with unknown value          {1: 2}                   {1: 2}
    Dict with unknown value          ${{{1: 2, '3': '4'}}}    {1: 2, 3: '4'}

Dict in union
    Dict in union 1                  {'a': '1'}               "{'a': '1'}"
    Dict in union 1                  ${STR TO STR}            ${STR TO STR}             same=True
    Dict in union 1                  ${STR TO INT}            "${STR TO INT}"
    Dict in union 2                  {'a': '1'}               "{'a': '1'}"
    Dict in union 2                  ${STR TO STR}            ${STR TO STR}             same=True
    Dict in union 2                  ${STR TO INT}            ${{dict($STR_TO_STR)}}

Incompatible dict
    [Template]                       Conversion should fail
    Dict                             {1: 2, 'bad': 'item'}    type=dict[int, float]     error=Key 'bad' cannot be converted to integer.
    Dict                             {1: 'bad'}               type=dict[int, float]     error=Item '1' got value 'bad' that cannot be converted to float.

Set
    Set                              set()                    set()
    Set                              {True}                   {True}
    Set                              {'kyllä', 'ei'}          {True, False}             # 'kyllä' and 'ei' conversions are due to language config.

Set with unknown
    Set with unknown                 set()                    set()
    Set with unknown                 {1, 2, 3}                {1, 2, 3}
    Set with unknown                 ${{['1', 2.0]}}          {'1', 2.0}

Set in union
    Set in union 1                   {'1', '2', '3'}          "{'1', '2', '3'}"
    Set in union 1                   ${{{'1', '2', '3'}}}     ${{{'1', '2', '3'}}}
    Set in union 1                   ${{{1, 2, 3}}}           "{1, 2, 3}"
    Set in union 2                   {'1', '2', '3'}          "{'1', '2', '3'}"
    Set in union 2                   ${{{'1', '2', '3'}}}     ${{{'1', '2', '3'}}}
    Set in union 2                   ${{{1, 2, 3}}}           ${{{'1', '2', '3'}}}

Incompatible set
    [Template]                       Conversion should fail
    Set                              {()}                     type=set[bool]            error=Item '()' (tuple) cannot be converted to boolean.

Nested generics
    Nested generics                  []                       []
    Nested generics                  [(1, 2)]                 [(1, 2)]
    Nested generics                  [('1', '2'), (3, 4)]     [(1, 2), (3, 4)]
    ${obj} =                         Evaluate                 [(1, 2), (3, 4), (5, -1)]
    Nested generics                  ${obj}                   ${obj}                    same=True

Incompatible nested generics
    [Template]                       Conversion should fail
    Nested generics                  1                        type=list[tuple[int, int]]
    ...    error=Value is integer, not list.
    Nested generics                  [1]                      type=list[tuple[int, int]]
    ...    error=Item '0' got value '1' (integer) that cannot be converted to tuple[int, int].
    Nested generics                  [(1, 'x')]               type=list[tuple[int, int]]
    ...    error=Item '0' got value '(1, 'x')' (tuple) that cannot be converted to tuple[int, int]: Item '1' got value 'x' that cannot be converted to integer.

Invalid list
    [Documentation]    FAIL    No keyword with name 'Invalid List' found.
    Invalid List    whatever

Invalid tuple
    [Documentation]    FAIL    No keyword with name 'Invalid Tuple' found.
    Invalid Tuple    whatever

Invalid dict
    [Documentation]    FAIL    No keyword with name 'Invalid Dict' found.
    Invalid Dict    whatever

Invalid set
    [Documentation]    FAIL    No keyword with name 'Invalid Set' found.
    Invalid Set    whatever

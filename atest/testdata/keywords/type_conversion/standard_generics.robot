language: fi

*** Settings ***
Library           StandardGenerics.py
Resource          conversion.resource
Force Tags        require-py3.9

*** Test Cases ***
List
    List                []                          []
    List                [1, 2, 3]                   [1, 2, 3]
    List                ['1', 2.0]                  [1, 2]

Incompatible list
    [Template]    Conversion should fail
    List                [1, 'bad']                  type=list[int]                  error=Item '1' got value 'bad' that cannot be converted to integer.
    List                [1, 2, 3.4]                 type=list[int]                  error=Item '2' got value '3.4' (float) that cannot be converted to integer: Conversion would lose precision.

Tuple
    Tuple               (1, 'true', 3.14)           (1, True, 3.14)
    Tuple               ('1', 'ei', '3.14')         (1, False, 3.14)    # 'ei' -> False conversion is due to language config.

Homogenous tuple
    Homogenous Tuple    ()                          ()
    Homogenous Tuple    (1,)                        (1,)
    Homogenous Tuple    (1, 2, '3', 4.0, 5)         (1, 2, 3, 4, 5)

Incompatible tuple
    [Template]    Conversion should fail
    Tuple               (1, 2, 'bad')               type=tuple[int, bool, float]    error=Item '2' got value 'bad' that cannot be converted to float.
    Homogenous Tuple    (1, '2', 3.0, 'four')       type=tuple[int, ...]            error=Item '3' got value 'four' that cannot be converted to integer.
    Tuple               ('too', 'few')              type=tuple[int, bool, float]    error=Expected 3 items, got 2.
    Tuple               ('too', 'many', '!', '!')   type=tuple[int, bool, float]    error=Expected 3 items, got 4.

Dict
    Dict                {}                           {}
    Dict                {1: 2}                       {1: 2}
    Dict                {1: 2, '3': 4.0}             {1: 2, 3: 4}

Incompatible dict
    [Template]    Conversion should fail
    Dict                {1: 2, 'bad': 'item'}        type=dict[int, float]          error=Key 'bad' cannot be converted to integer.
    Dict                {1: 'bad'}                   type=dict[int, float]          error=Item '1' got value 'bad' that cannot be converted to float.

Set
    Set                 set()                        set()
    Set                 {True}                       {True}
    Set                 {'kyllä', 'ei'}              {True, False}    # 'kyllä' and 'ei' conversions are due to language config.

Incompatible set
    [Template]    Conversion should fail
    Set                 {()}                         type=set[bool]                 error=Item '()' (tuple) cannot be converted to boolean.

Invalid list
    [Documentation]     FAIL    TypeError: list[] construct used as a type hint requires exactly 1 nested type, got 2.
    Invalid List        whatever

Invalid tuple
    [Documentation]     FAIL    TypeError: Homogenous tuple used as a type hint requires exactly one nested type, got 2.
    Invalid Tuple       whatever

Invalid dict
    [Documentation]     FAIL    TypeError: dict[] construct used as a type hint requires exactly 2 nested types, got 1.
    Invalid Dict        whatever

Invalid set
    [Documentation]     FAIL    TypeError: set[] construct used as a type hint requires exactly 1 nested type, got 2.
    Invalid set         whatever

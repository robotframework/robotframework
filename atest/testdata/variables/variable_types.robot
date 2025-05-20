*** Settings ***
Library         ../test_libraries/Embedded.py
Variables       extended_variables.py


*** Variables ***
${INTEGER: int}                         42
${INT_LIST: list[int]}                  [42, '1']
${EMPTY_STR: str}                       ${EMPTY}
@{LIST: int}                            1    ${2}    3
@{LIST_IN_LIST: list[int]}              [1, 2]    ${LIST}
${NONE_TYPE: None}                      None
&{DICT_1: str=int|str}                  a=1    b=${2}    c=${None}
&{DICT_2: int=list[int]}                1=[1, 2, 3]    2=[4, 5, 6]
&{DICT_3: list[int]}                    10=[3, 2]    20=[1, 0]
${NO_TYPE}                              42
${BAD_VALUE: int}                       not int
${BAD_TYPE: hahaa}                      1
@{BAD_LIST_VALUE: int}                  1    hahaa
@{BAD_LIST_TYPE: xxxxx}                 k    a    l    a
&{BAD_DICT_VALUE: str=int}              x=a    y=b
&{BAD_DICT_TYPE: aa=bb}                 x=1    y=2
&{INVALID_DICT_TYPE1: int=list[int}     1=[1, 2, 3]    2=[4, 5, 6]
&{INVALID_DICT_TYPE2: int=listint]}     1=[1, 2, 3]    2=[4, 5, 6]
${NAME}                                 NO_TYPE_FROM_VAR: int
${${NAME}}                              42


*** Test Cases ***
Command line
    Should Be Equal    ${CLI}     2025-05-20    type=date
    Should Be Equal    ${NOT}     INT:1
    Should Be Equal    ${NOT2}    ${SPACE}leading space, no 2nd colon

Variable section
    Should be equal    ${INTEGER}    42    type=int
    Variable should not exist    ${INTEGER: int}
    Should be equal    ${INT_LIST}    [42, 1]    type=list
    Variable should not exist    ${INT_LIST: list[int]}
    Should be equal    ${EMPTY_STR}    ${EMPTY}
    Variable should not exist    ${EMPTY_STR: str}
    Should be equal    ${NO_TYPE}    42
    Should be equal    ${NONE_TYPE}    ${None}
    Variable should not exist    ${NONE_TYPE: None}
    Should be equal    ${NO_TYPE_FROM_VAR: int}    42    type=str

Variable section: List
    Should be equal    ${LIST_IN_LIST}    [[1, 2], [1, 2, 3]]    type=list
    Variable should not exist    ${LIST_IN_LIST: list[int]}
    Should be equal    ${LIST}    ${{[1, 2, 3]}}
    Variable should not exist    ${LIST: int}

Variable section: Dictionary
    Should be equal    ${DICT_1}    {"a": "1", "b": 2, "c": "None"}    type=dict
    Variable should not exist    ${DICT_1: str=int|str}
    Should be equal    ${DICT_2}    {1: [1, 2, 3], 2: [4, 5, 6]}    type=dict
    Variable should not exist    ${DICT_2: int=list[int]}
    Should be equal    ${DICT_3}    {"10": [3, 2], "20": [1, 0]}    type=dict
    Variable should not exist    ${DICT_3: list[int]}

Variable section: With invalid values or types
    Variable should not exist    ${BAD_VALUE}
    Variable should not exist    ${BAD_VALUE: int}
    Variable should not exist    ${BAD_TYPE}
    Variable should not exist    ${BAD_TYPE: hahaa}
    Variable should not exist    ${BAD_LIST_VALUE}
    Variable should not exist    ${BAD_LIST_VALUE: int}
    Variable should not exist    ${BAD_LIST_TYPE}
    Variable should not exist    ${BAD_LIST_TYPE: xxxxx}
    Variable should not exist    ${BAD_DICT_VALUE}
    Variable should not exist    ${BAD_DICT_VALUE: str=int}
    Variable should not exist    ${BAD_DICT_TYPE}
    Variable should not exist    ${BAD_DICT_TYPE: aa=bb}
    Variable should not exist    ${INVALID_DICT_TYPE1}
    Variable should not exist    ${INVALID_DICT_TYPE1: int=list[int}
    Variable should not exist    ${INVALID_DICT_TYPE2}
    Variable should not exist    ${INVALID_DICT_TYPE2: int=listint]}

VAR syntax
    VAR    ${x: int|float}    123
    Should be equal    ${x}    123    type=int
    VAR    ${x: int}    1    2    3    separator=
    Should be equal    ${x}    123    type=int
    VAR    ${name}    x
    VAR    ${${name}: int}    432
    Should be equal    ${x}    432    type=int

VAR syntax: List
    VAR    ${x: list}    [1, "2", 3]
    Should be equal    ${x}    [1, "2", 3]    type=list
    VAR    @{x: int}    1    2    3
    Should be equal    ${x}    [1, 2, 3]    type=list
    VAR    @{x: list[int]}    [1, 2]    [2, 3, 4]
    Should be equal    ${x}    [[1, 2], [2, 3, 4]]    type=list

VAR syntax: Dictionary
    VAR    &{x: int}    1=2    3=4
    Should be equal    ${x}    {"1": 2, "3": 4}    type=dict
    VAR    &{x: int=str}    3=4    5=6
    Should be equal    ${x}    {3: "4", 5: "6"}    type=dict
    VAR    &{x: int = str}    100=200    300=400
    Should be equal    ${x}    {100: "200", 300: "400"}    type=dict
    VAR    &{x: int=dict[str, float]}    30={"key": 1}    40={"key": 2.3}
    Should be equal    ${x}    {30: {"key": 1.0}, 40: {"key": 2.3}}    type=dict

VAR syntax: Invalid scalar value
    [Documentation]    FAIL
    ...    Setting variable '\${x: int}' failed: Value 'KALA' cannot be converted to integer.
    VAR    ${x: int}    KALA

VAR syntax: Invalid scalar type
    [Documentation]    FAIL    Invalid variable '\${x: hahaa}': Unrecognized type 'hahaa'.
    VAR    ${x: hahaa}    KALA

VAR syntax: Type can not be set as variable
    [Documentation]    FAIL    Invalid variable '\${x: \${type}}': Unrecognized type '\${type}'.
    VAR    ${type}    int
    VAR    ${x: ${type}}    1

VAR syntax: Type syntax is not resolved from variable
    VAR    ${type}    : int
    VAR    ${safari${type}}    42
    Should be equal    ${safari: int}    42    type=str
    VAR    ${type}    tidii: int
    VAR    ${${type}}    4242
    Should be equal    ${tidii: int}    4242    type=str

Variable assignment
    ${x: int} =    Set Variable    42
    Should be equal    ${x}    42    type=int

Variable assignment: List
    @{x: int} =    Create List    1    2    3
    Should be equal    ${x}    [1, 2, 3]    type=list
    @{x: list[INT]} =    Create List    [1, 2]    [2, 3, 4]
    Should be equal    ${x}    [[1, 2], [2, 3, 4]]    type=list
    ${x: list[integer]} =    Create List    1    2    3
    Should be equal    ${x}    [1, 2, 3]    type=list

Variable assignment: Dictionary
    &{x: int} =    Create Dictionary    1=2    ${3}=${4.0}
    Should be equal    ${x}    {"1": 2, 3: 4}    type=dict
    &{x: int=str} =    Create Dictionary    1=2    ${3}=${4.0}
    Should be equal    ${x}    {1: "2", 3: "4.0"}    type=dict
    ${x: dict[str, int]} =    Create dictionary    1=2    3=4
    Should be equal    ${x}    {"1": 2, "3": 4}    type=dict
    &{x: int=dict[str, int]} =    Create Dictionary    1={2: 3}    4={5: 6}
    Should be equal    ${x}    {1: {"2": 3}, 4: {"5": 6}}    type=dict

Variable assignment: Invalid value
    [Documentation]    FAIL
    ...    ValueError: Return value 'kala' cannot be converted to list[int]: \
    ...    Invalid expression.
    ${x: list[int]} =    Set Variable    kala

Variable assignment: Invalid type
    [Documentation]    FAIL Unrecognized type 'not_a_type'.
    ${x: list[not_a_type]} =    Set Variable    1    2

Variable assignment: Invalid variable type for list
    [Documentation]    FAIL
    ...    ValueError: Return value '['1', '2', '3']' (list) cannot be converted to float.
    ${x: float} =    Create List    1    2    3

Variable assignment: Invalid type for list
    [Documentation]    FAIL
    ...    ValueError: Return value '['1', '2', '3']' (list) cannot be converted to list[list[int]]: \
    ...    Item '0' got value '1' that cannot be converted to list[int]: Value is integer, not list.
    @{x: list[int]} =    Create List    1    2    3

Variable assignment: Invalid variable type for dictionary
    [Documentation]    FAIL    Unrecognized type 'int=str'.
    ${x: int=str} =    Create dictionary    1=2    3=4

Variable assignment: Multiple
    ${a: int}    ${b: float} =    Create List    1    2.3
    Should be equal    ${a}    1      type=int
    Should be equal    ${b}    2.3    type=float

Variable assignment: Multiple list and scalars
    ${a: int}    @{b: float} =    Create List    1    2    3.4
    Should be equal    ${a}    1             type=int
    Should be equal    ${b}    [2.0, 3.4]    type=list
    @{a: int}    ${b: float} =    Create List    1    2    3.4
    Should be equal    ${a}    [1, 2]    type=list
    Should be equal    ${b}    3.4       type=float
    ${a: int}    @{b: float}    ${c: float} =    Create List    1    2    3.4
    Should be equal    ${a}    1        type=int
    Should be equal    ${b}    [2.0]    type=list
    Should be equal    ${c}    3.4      type=float
    ${a: int}    @{b: float}    ${c: float}    ${d: float} =    Create List    1    2    3.4
    Should be equal    ${a}    1      type=int
    Should be equal    ${b}    []     type=list
    Should be equal    ${c}    2.0    type=float
    Should be equal    ${d}    3.4    type=float

Variable assignment: Invalid type for list in multiple variable assignment
    [Documentation]    FAIL    Unrecognized type 'bad'.
    ${a: int}    @{b: bad} =    Create List    9    8    7

Variable assignment: Type can not be set as variable
    [Documentation]    FAIL    Unrecognized type '\${type}'.
    VAR    ${type}    int
    ${a: ${type}} =    Set variable    123

Variable assignment: Type syntax is not resolved from variable
    VAR    ${type}    x: int
    ${${type}} =    Set variable    12
    Should be equal    ${x: int}    12

Variable assignment: Extended
    [Documentation]    FAIL    ValueError: Return value 'kala' cannot be converted to integer.
    Should be equal    ${OBJ.name}    dude
    ${OBJ.name: int} =    Set variable    42
    Should be equal    ${OBJ.name}    42    type=int
    ${OBJ.name: int} =    Set variable    kala

Variable assignment: Item
    [Documentation]    FAIL    ValueError: Return value 'kala' cannot be converted to integer.
    VAR    @{x}    1    2
    ${x: int}[0] =    Set variable    3
    Should be equal    ${x}    [3, "2"]    type=list
    ${x: int}[0] =    Set variable    kala

User keyword
    Keyword    1    1    int
    Keyword    1.2    1.2    float
    Varargs    1    2    3
    Kwargs    a=1    b=2.3
    Combination of all args    1.0    2    3    4    a=5    b=6

User keyword: Default value
    Default
    Default    1
    Default as string
    Default as string    ${42}

User keyword: Wrong default value 1
    [Documentation]    FAIL
    ...    ValueError: Argument default value 'arg' got value 'wrong' that cannot be converted to integer.
    Wrong default

User keyword: Wrong default value 2
    [Documentation]    FAIL
    ...    ValueError: Argument 'arg' got value 'yyy' that cannot be converted to integer.
    Wrong default    yyy

User keyword: Invalid value
    [Documentation]    FAIL
    ...    ValueError: Argument 'type' got value 'bad' that cannot be \
    ...    converted to 'int', 'float' or 'third value in literal'.
    Keyword    1.2    1.2    bad

User keyword: Invalid type
    [Documentation]    FAIL
    ...    Invalid argument specification: \
    ...    Invalid argument '\${arg: bad}': \
    ...    Unrecognized type 'bad'.
    Bad type

User keyword: Invalid assignment with kwargs k_type=v_type declaration
    [Documentation]    FAIL
    ...    Invalid argument specification: \
    ...    Invalid argument '\&{kwargs: int=float}': \
    ...    Unrecognized type 'int=float'.
    Kwargs does not support key=value type syntax

Embedded arguments
    Embedded 1 and 2
    Embedded type 1 and no type 2
    Embedded type with custom regular expression 111

Embedded arguments: With variables
    VAR    ${x}    1
    VAR    ${y}    ${2.0}
    Embedded ${x} and ${y}

Embedded arguments: Invalid value
    [Documentation]    FAIL    ValueError: Argument 'kala' cannot be converted to integer.
    Embedded 1 and kala

Embedded arguments: Invalid value from variable
    [Documentation]    FAIL    ValueError: Argument '[2, 3]' (list) cannot be converted to integer.
    Embedded 1 and ${{[2, 3]}}

Embedded arguments: Invalid type
    [Documentation]    FAIL    Invalid embedded argument '\${x: invalid}': Unrecognized type 'invalid'.
    Embedded invalid type ${x: invalid}

Variable usage does not support type syntax 1
    [Documentation]    FAIL    STARTS: Resolving variable '\${x: int}' failed: SyntaxError:
    VAR    ${x}    1
    Log    This fails: ${x: int}

Variable usage does not support type syntax 2
    [Documentation]    FAIL
    ...    Resolving variable '\${abc_not_here: int}' failed: \
    ...    Variable '\${abc_not_here}' not found.
    Log    ${abc_not_here: int}: fails

FOR
    VAR    ${expected: int}    1
    FOR    ${item: int}    IN    1    2    3
        Should Be Equal    ${item}    ${expected}
        ${expected} =    Evaluate    ${expected} + 1
    END

FOR: Multiple variables
    VAR    @{english}    cat      dog      horse
    VAR    @{finnish}    kissa    koira    hevonen
    VAR    ${index: int}    1
    FOR    ${i: int}    ${en: Literal["cat", "dog", "horse"]}    ${fi: str}    IN
    ...    1    cat      kissa
    ...    2    Dog      koira
    ...    3    HORSE    hevonen
        Should Be Equal    ${i}     ${index}
        Should Be Equal    ${en}    ${english}[${index-1}]
        Should Be Equal    ${fi}    ${finnish}[${index-1}]
        ${index} =    Evaluate    ${index} + 1
    END

FOR: Dictionary
    VAR    &{dict}    1=2    3=4
    VAR    ${index: int}    1
    FOR    ${key: int}    ${value: int}    IN    &{dict}    5=6
        Should Be Equal    ${key}      ${index}
        Should Be Equal    ${value}    ${index + 1}
        ${index} =    Evaluate    ${index} + 2
    END
    VAR    ${index: int}    1
    FOR    ${item: tuple[int, int]}    IN    1=ignored    &{dict}    5=6
        Should Be Equal    ${item}      ${{($index, $index+1)}}
        ${index} =    Evaluate    ${index} + 2
    END

FOR IN RANGE
    VAR    ${expected: int}    0
    FOR    ${x: timedelta}    IN RANGE    10
        Should Be Equal    ${x.total_seconds()}    ${expected}
        ${expected} =    Evaluate    ${expected} + 1
    END

FOR IN ENUMERATE
    VAR    ${index: int}    0
    FOR    ${i: str}    ${x: int}    IN ENUMERATE    0    1    2    3    4    5
        Should Be Equal    ${i}    ${index}    type=str
        Should Be Equal    ${x}    ${index}    type=int
        ${index} =    Evaluate    ${index} + 1
    END
    VAR    ${index: int}    1
    FOR    ${item: tuple[str, int]}    IN ENUMERATE    1    2    3    start=1
        Should Be Equal    ${item}    ${{($index, $index)}}    type=tuple[str, int]
        ${index} =    Evaluate    ${index} + 1
    END

FOR IN ENUMERATE: Dictionary
    VAR    &{dict}    0=1    1=${2}    ${2}=3
    VAR    ${index: int}    0
    FOR    ${i: str}    ${key: int}    ${value: int}    IN ENUMERATE    &{dict}
        Should Be Equal    ${i}        ${index}    type=str
        Should Be Equal    ${key}      ${index}
        Should Be Equal    ${value}    ${index + 1}
        ${index} =    Evaluate    ${index} + 1
    END
    VAR    ${index: int}    0
    FOR    ${i: str}    ${item: tuple[int, int]}    IN ENUMERATE    &{dict}    3=${4.0}
        Should Be Equal    ${i}       ${index}    type=str
        Should Be Equal    ${item}    ${{($index, $index+1)}}    type=tuple[int, int]
        ${index} =    Evaluate    ${index} + 1
    END
    VAR    ${index: int}    0
    FOR    ${all: list[str]}    IN ENUMERATE    0=ignore    &{dict}    3=4    ${4}=${5}
        Should Be Equal    ${all}    ${{[$index, $index, $index+1]}}    type=list[str]
        ${index} =    Evaluate    ${index} + 1
    END

FOR IN ZIP
    VAR    @{list1}    ${1}    ${2}    ${3}
    VAR    @{list2}    1    2    3
    VAR    ${index: int}    1
    FOR    ${i1: str}    ${i2: int}    IN ZIP    ${list1}    ${list2}
        Should Be Equal    ${i1}    ${index}    type=str
        Should Be Equal    ${i2}    ${index}
        ${index} =    Evaluate    ${index} + 1
    END
    VAR    ${index: int}    1
    FOR    ${item: tuple[str, int]}    IN ZIP    ${list1}    ${list2}
        Should Be Equal    ${item}    ${{($index, $index)}}    type=tuple[str, int]
        ${index} =    Evaluate    ${index} + 1
    END

FOR: Failing conversion 1
    [Documentation]    FAIL
    ...    ValueError: FOR loop variable '\${x: float}' got value 'bad' \
    ...    that cannot be converted to float.
    FOR    ${x: float}    IN    1    bad    3
        Should Be Equal    ${x}    1    type=float
    END

FOR: Failing conversion 2
    [Documentation]    FAIL
    ...    ValueError: FOR loop variable '\${x: int}' got value '0.1' (float) \
    ...    that cannot be converted to integer: Conversion would lose precision.
    FOR    ${x: int}    IN RANGE    0    1    0.1
        Should Be Equal    ${x}    0    type=int
    END

FOR: Failing conversion 3
    [Documentation]    FAIL
    ...    ValueError: FOR loop variable '\${i: Literal[0, 1, 2]}' got value '3' (integer) \
    ...    that cannot be converted to 0, 1 or 2.
    VAR    ${expected: int}    0
    FOR    ${i: Literal[0, 1, 2]}    ${c: Literal["a", "b", "c"]}    IN ENUMERATE    a    B    c    d    e
        Should Be Equal    ${i}    ${expected}
        Should Be Equal    ${c}    ${{"abc"[$expected]}}
        ${expected} =    Evaluate    ${expected} + 1
    END

FOR: Invalid type
    [Documentation]    FAIL
    ...    Invalid FOR loop variable '\${item: bad}': Unrecognized type 'bad'.
    FOR    ${item: bad}    IN ENUMERATE    whatever
        Fail    Not run
    END

Inline IF
    ${x: int} =    IF    True    Default as string    ELSE    Default
    Should be equal    ${x}    42    type=int
    ${x: str} =    IF    False    Default as string    ELSE    Default
    Should be equal    ${x}    1    type=str
    ${first: int}    @{rest: int | float} =    IF    True    Create List    1    2.3    4
    Should be equal    ${first}    1    type=int
    Should be equal    ${rest}    [2.3, 4]    type=list
    @{x: int} =    IF    False    Fail    Not run
    Should be equal    ${x}    []    type=list

Set global/suite/test/local variable: No support
    Set local variable    ${local: int}     1
    Should be equal       ${local: int}     1    type=str
    Set test variable     ${test: xxx}      2
    Should be equal       ${test: xxx}      2    type=str
    Set suite variable    ${suite: int}     3
    Should be equal       ${suite: int}     3    type=str
    Set suite variable    ${global: int}    4
    Should be equal       ${global: int}    4    type=str


*** Keywords ***
Keyword
    [Arguments]    ${arg: int|float}    ${exp}    ${type: Literal['int', 'float', 'third value in literal']}
    Should be equal    ${arg}    ${exp}    type=${type}

Varargs
    [Arguments]    @{args: int}
    Should be equal    ${args}    [1, 2, 3]    type=list

Kwargs
    [Arguments]    &{args: float|int}
    Should be equal    ${args}    {"a":1, "b":2.3}    type=dict

Default
    [Arguments]    ${arg: int}=1
    Should be equal    ${arg}    1    type=int
    RETURN    ${arg}

Default as string
    [Arguments]    ${arg: str}=${42}
    Should be equal    ${arg}    42    type=str
    RETURN    ${arg}

Wrong default
    [Arguments]    ${arg: int}=wrong
    Fail    This shuld not be run

Bad type
    [Arguments]    ${arg: bad}
    Fail    Should not be run

Kwargs does not support key=value type syntax
    [Arguments]    &{kwargs: int=float}
    Variable should not exist    &{kwargs}

Combination of all args
    [Arguments]    ${arg: float}    @{args: int}    &{kwargs: int}
    Should be equal    ${arg}    1.0    type=float
    Should be equal    ${args}    [2, 3, 4]    type=list[int]
    Should be equal    ${kwargs}    {"a": 5, "b": 6}    type=dict[str, int]

Embedded ${x: int} and ${y: int}
    Should be equal    ${x}    1    type=int
    Should be equal    ${y}    2    type=int

Embedded type ${x: int} and no type ${y}
    Should be equal    ${x}    1    type=int
    Should be equal    ${y}    2    type=str

Embedded type with custom regular expression ${x:.+: int}
    Should be equal    ${x}    111    type=int

Embedded invalid type ${x: invalid}
    Fail    Should not be run

*** Variables ***
${INTEGER: int}                         42
${INT_LIST: list[int]}                  [42, '1']
${EMPTY_STR: str}                       ${EMPTY}
@{LIST: int}                            1    2    3
@{LIST_IN_LIST: list[int]}              [1, 2]    [3, 4]
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


*** Test Cases ***
Variable section
    Should be equal    ${INTEGER}    ${42}
    Variable should not exist    ${INTEGER: int}
    Should be equal    ${INT_LIST}    [42, 1]    type=list[int]
    Variable should not exist    ${INT_LIST: list[int]}
    Should be equal    ${EMPTY_STR}    ${EMPTY}
    Variable should not exist    ${EMPTY_STR: str}
    Should be equal    ${LIST_IN_LIST}    [[1, 2], [3, 4]]    type=list[list[int]]
    Variable should not exist    ${LIST_IN_LIST: list[int]}
    Should be equal    ${LIST}    ${{[1, 2, 3]}}
    Variable should not exist    ${LIST: int}
    Should be equal    ${DICT_1}    {"a": "1", "b": 2, "c": "None"}    type=dict[str, int|str]
    Variable should not exist    ${DICT_1: str=int|str}
    Should be equal    ${DICT_2}    {1: [1, 2, 3], 2: [4, 5, 6]}    type=dict[int, list[int]]
    Variable should not exist    ${DICT_2: int=list[int]}
    Should be equal    ${DICT_3}    {"10": [3, 2], "20": [1, 0]}    type=dict[str, list[int]]
    Variable should not exist    ${DICT_3: list[int]}
    Should be equal    ${NO_TYPE}    42
    Should be equal    ${NONE_TYPE}    ${None}
    Variable should not exist    ${NO_TYPE: None}

Variables with invalid values or types
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
    Should be equal    ${x}    ${123}
    VAR    ${x: list}    [1, "2", 3]
    Should be equal    ${x}    [1, "2", 3]    type=list
    VAR    ${x: int}    1    2    3    separator=
    Should be equal    ${x}    ${123}
    VAR    @{x: int}    1    2    3
    Should be equal    ${x}    [1, 2, 3]    type=list[int]
    VAR    @{x: list[int]}    [1, 2]    [2, 3, 4]
    Should be equal    ${x}    [[1, 2], [2, 3, 4]]    type=list[list[int]]
    VAR    &{x: int}    1=2    3=4
    Should be equal    ${x}    {"1": 2, "3": 4}    type=dict[str, int]
    VAR    &{x: int=str}    3=4    5=6
    Should be equal    ${x}    {3: "4", 5: "6"}    type=dict[int, str]
    VAR    &{x: int=dict[str, float]}    30={"key": 1}    40={"key": 2.3}
    Should be equal    ${x}    {30: {"key": 1.0}, 40: {"key": 2.3}}    type=dict[int, dict[str, float]]

Invalid VAR syntax value as scalar
    [Documentation]    FAIL Setting variable '\${x: int}' failed: Value 'KALA' cannot be converted to integer.
    VAR    ${x: int}    KALA

Invalid VAR syntax type as scalar
    [Documentation]    FAIL Setting variable '\${x: hahaa}' failed: Unrecognized type 'hahaa'.
    VAR    ${x: hahaa}    KALA

Single variable assignment
    [Tags]    kala
    ${x: int} =    Set Variable    42
    Should be equal    ${x}    ${42}
    @{x} =    Create List    1    2    3
    Should be equal    ${x}    ["1", "2", "3"]    type=list[str]
    @{x: int} =    Create List    1    2    3
    Should be equal    ${x}    [1, 2, 3]    type=list[int]
    @{x: list[int]} =    Create List    [1, 2]    [2, 3, 4]
    Should be equal    ${x}    [[1, 2], [2, 3, 4]]    type=list[list[int]]
    ${x: list[int]} =    Create List    1    2    3
    Should be equal    ${x}    [1, 2, 3]    type=list[int]
    &{x: int} =    Create Dictionary    1=2    3=4
    Should be equal    ${x}    ${{{"1": 2, "3": 4}}}
    &{x: int=str} =    Create Dictionary    1=2    3=4
    Should be equal    ${x}    {1: "2", 3: "4"}    type=dict[int, str]
    ${x: dict[str, int]} =    Create dictionary    1=2    3=4
    Should be equal    ${x}    {"1": 2, "3": 4}    type=dict[str, int]
    &{x: int=dict[str, int]} =    Create Dictionary    1={2: 3}    4={5: 6}
    Should be equal    ${x}    {1: {"2": 3}, 4: {"5": 6}}    type=dict[int, dict[str, int]]

Invalid value single variable assignment
    [Documentation]    FAIL ValueError: Return value 'kala' cannot be converted to list[int]: Invalid expression.
    ${x: list[int]} =    Set Variable    kala

Invalid type single variable assignment
    [Documentation]    FAIL TypeError: Unrecognized type 'not_a_type'.
    ${x: list[not_a_type]} =    Set Variable    1    2

Invalid type single variable assignment as list
    [Documentation]    FAIL ValueError: Return value '['1', '2', '3']' (list) cannot be converted to list[list[int]]: Item '0' got value '1' that cannot be converted to list[int]: Value is integer, not list.
    @{x: list[int]} =    Create List    1    2    3

Invalid type single variable assignment from scalar to list
    [Documentation]    FAIL ValueError: Return value '['1', '2', '3']' (list) cannot be converted to float.
    ${x: float} =    Create List    1    2    3

Invalid type single variable assignment from scalar to dictionary
    [Documentation]    FAIL TypeError: Unrecognized type 'int=str'.
    ${x: int=str} =    Create dictionary    1=2    3=4

Multi variable assignment
    ${a: int}    ${b: float} =    Create List    1    2.3
    Should be equal    ${a}    ${1}
    Should be equal    ${b}    ${2.3}
    ${a: int}    @{b: float} =    Create List    1    2    3.4
    Should be equal    ${a}    ${1}
    Should be equal    ${b}    [2.0, 3.4]    type=list[float]
    @{a: int}    ${b: float} =    Create List    1    2    3.4
    Should be equal    ${a}    [1, 2]    type=list[int]
    Should be equal    ${b}    ${3.4}
    ${a: int}    @{b: float}    ${c: float} =    Create List    1    2    3.4
    Should be equal    ${a}    ${1}
    Should be equal    ${b}    [2.0]    type=list[float]
    Should be equal    ${c}    ${3.4}

Invalid multi variable assignment
    [Documentation]    FAIL TypeError: Unrecognized type 'no_type'.
    ${a: int}    @{b: no_type} =    Create List    9    8    7

Assignment
    Keyword    1    ${1}    int|float
    Varargs    1    2    3
    Kwargs    a=1    b=2.3
    Combination of all args    1.0    2    3    4    a=5    b=6

Invalid assignment with kwargs k_type=v_type declaration
    [Documentation]    FAIL Keyword 'Kwargs type and value is not possible' expected 0 arguments, got 2.
    Kwargs type and value is not possible    1=2.3    4=5.6

Set global/suite/test/local variable
    ${local_v: int}    Set variable    1
    Should be equal    ${local_v}    1    type=int
    Set test variable    ${test_v: int}    2
    Should be equal    ${test_v}    2    type=int
    Set suite variable    ${suite_v: int}    3
    Should be equal    ${suite_v}    3    type=int
    Set suite variable    ${global_v: int}    4
    Should be equal    ${global_v}    4    type=int

Logging
    [Documentation]    FAIL Variable '${0b123}' not found.
    Log    This should not work: ${0b123}

*** Keywords ***
Keyword
    [Arguments]    ${arg: int|float}    ${exp}    ${type}
    Should be equal    ${arg}    ${exp}    type=${type}

Varargs
    [Arguments]    @{args: int}
    Should be equal    ${args}    [1, 2, 3]    type=list[int]

Kwargs
    [Arguments]    &{args: float|int}
    Should be equal    ${args}    {"a":1, "b":2.3}    type=dict[str, int|float]

Kwargs type and value is not possible
    [Arguments]    &{kwargs: int=float}
    Variable should not exist    &{kwargs}

Combination of all args
    [Arguments]    ${arg: float}    @{args: int}    &{kwargs: int}
    Should be equal    ${arg}    1.0    type=float
    Should be equal    ${args}    [2, 3, 4]    type=list[int]
    Should be equal    ${kwargs}    {"a": 5, "b": 6}    type=dict[str, int]

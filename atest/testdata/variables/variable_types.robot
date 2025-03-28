*** Variables ***
${INTEGER: int}               42
${INT_LIST: list[int]}        [42, '1']
@{LIST: int}                  1    2    3
&{DICT_1: str=int|str}        a=1    b=${2}    c=${None}
&{DICT_2: int=list[int]}      1=[1, 2, 3]    2=[4, 5, 6]
${NO_TYPE}                    42
${BAD_VALUE: int}             hahaa
${BAD_TYPE: hahaa}            1
@{BAD_LIST_VALUE: int}        1    hahaa
@{BAD_LIST_TYPE: xxxxx}       k    a    l    a
&{BAD_DICT_VALUE: str=int}    x=1    y=2
&{BAD_DICT_TYPE: ha=haa}      x=1    y=2

*** Test Cases ***
Variable section
    Should Be Equal    ${INTEGER}    ${42}
    Should Be Equal    ${INT_LIST}    ${{[42, 1]}}
    Should Be Equal    ${LIST}    ${{[1, 2, 3]}}
    Should Be Equal    ${DICT_1}    ${{{"a": "1", "b": 2, "c": "None"}}}
    Should Be Equal    ${DICT_2}    ${{{1: [1, 2, 3], 2: [4, 5, 6]}}}
    Should Be Equal    ${NO_TYPE}    42

Variables with invalid values or types
    Variable should not exist    ${BAD_VALUE}
    Variable should not exist    ${BAD_TYPE}
    Variable should not exist    ${BAD_LIST_VALUE}
    Variable should not exist    ${BAD_LIST_TYPE}
    Variable should not exist    ${BAD_DICT_VALUE}
    Variable should not exist    ${BAD_DICT_TYPE}

VAR syntax
    VAR    ${x: int|float}    123
    Should be equal    ${x}    ${123}
    VAR    ${x: list}    [1, "2", 3]
    Should be equal    ${x}    ${{[1, "2", 3]}}
    VAR    ${x: int}    1    2    3    separator=
    Should be equal    ${x}    ${123}

Invalid VAR syntax value
    [Documentation]    FAIL Setting variable '\${x: int}' failed: Value 'KALA' cannot be converted to integer.
    VAR    ${x: int}    KALA

Invalid VAR syntax type
    [Documentation]    FAIL Setting variable '\${x: hahaa}' failed: Cannot convert type 'hahaa'.
    VAR    ${x: hahaa}    KALA

Single variable assignment
    ${x: int} =    Set Variable    42
    Should be equal    ${x}    ${42}
    ${x: list[int]} =    Create List    1   2   3
    Should be equal    ${x}    ${{[1, 2, 3]}}
    @{x: list[int]} =    Create List    1   2   3
    Should be equal    ${x}    ${{[1, 2, 3]}}

Invalid value single variable assignment
    [Documentation]    FAIL ValueError: Return value 'kala' cannot be converted to list[int]: Invalid expression.
    ${x: list[int]} =    Set Variable    kala

Invalid type single variable assignment
    [Documentation]    FAIL ValueError: Return value 'kala' cannot be converted to list[int]: Invalid expression.
    ${x: list[hahaa]} =    Set Variable    1    2

Multi variable assignment
    ${a: int}    ${b: float} =    Create List    1   2.3
    Should be equal    ${a}    ${1}
    ${a: int}    @{b: float} =    Create List    1   2    3.4
    Should be equal    ${a}    ${1}
    Should be equal    ${b}    ${{[2.0, 3.4]}}
    @{a: int}    ${b: float} =    Create List    1   2    3.4
    Should be equal    ${a}    ${{[1, 2]}}
    Should be equal    ${b}    ${3.4}
    ${a: int}    @{b: float}    ${c: float}=    Create List    1   2    3.4
    Should be equal    ${a}    ${1}
    Should be equal    ${b}    ${{[2.0]}}
    Should be equal    ${c}    ${3.4}

Invalid list assignment
    [Documentation]    FAIL ValueError: Return value '['1', '2', '3']' (list) cannot be converted to float.
    ${x: float} =    Create List    1   2   3

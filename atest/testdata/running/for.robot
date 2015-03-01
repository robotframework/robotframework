*** Settings ***
Documentation  NO RIDE because we want to test different formatting
Variables   binary_list.py

*** Variables ***
@{NUMS}           1    2    3    4    5
@{RESULT}
${NO VALUES}      FOR loop has no loop values.
${NO KEYWORDS}    FOR loop contains no keywords.
${NO VARIABLES}   FOR loop has no loop variables.
${WRONG VALUES}   Number of FOR loop values should be multiple of variables.

*** Test Cases ***
Simple For
    Log    Not yet in For
    : FOR    ${var}    IN    one    two
    \    Log    var: ${var}
    Log    Not in For anymore

Simple For 2
    : FOR    ${num}    IN    @{NUMS}    6
    \    Log    ${num}
    \    Log    Hello from for loop
    \    No Operation
    \    Run Keyword If    ${num} in [2,6]    Log    Presidential Candidate!    WARN

Empty For Body Fails
    [Documentation]    FAIL    ${NO KEYWORDS}
    : FOR    ${var}    IN    one    two
    Fail    Not executed

For Without Value Fails
    [Documentation]    FAIL    ${NO VALUES}
    : FOR    ${var}    IN
    \    Fail    not executed
    Fail    Not executed

For Loop Over Empty List Variable Is Ok
    : FOR    ${var}    IN    @{EMPTY}
    \    Fail    not executed
    Variable Should Not Exist    ${var}

For Failing 1
    [Documentation]    FAIL    Here we fail!
    : FOR    ${num}    IN    @{NUMS}
    \    Log    Hello before failing kw
    \    Fail    Here we fail!
    \    Fail    Not executed
    Fail    Not executed

For Failing 2
    [Documentation]    FAIL    Failure with 4
    : FOR    ${num}    IN    @{NUMS}
    \    Log    Before Check
    \    Should Not Be Equal    ${num}    4    Failure with ${num}    no values
    \    Log    After Check
    Fail    Not executed

For With Values On Multiple Rows
    : FOR    ${i}    IN    @{NUMS}    6    7    8
    ...    9    10
    \    Log    ${i}
    Should Be Equal    ${i}    10

For With Keyword Args On Multiple Rows
    : FOR    ${var}    IN    one    two
    \    ${msg} =    Catenate    1    2    3    4
    \    ...    5    6    7    ${var}
    \    Log    ${msg}
    \    Should Be Equal    ${msg}    1 2 3 4 5 6 7 ${var}

Many Fors In One Test
    : FOR    ${x}    IN    foo    bar
    \    Log    In first for with var "${x}"
    : FOR    ${y}    IN    Hello, world!
    \    My UK 2    ${y}
    Log    Outside for loop
    : FOR    ${z}    IN    a    b
    \    Log    Third for loop
    \    No operation
    \    Log    Value: ${z}
    Log    End of the test

For With User Keywords
    [Documentation]    FAIL    Fail outside for
    : FOR    ${x}    IN    foo    bar
    \    My UK
    \    My UK 2    ${x}
    Fail    Fail outside for

For With Failures In User Keywords
    [Documentation]    FAIL    Failure with 2
    : FOR    ${num}    IN    @{NUMS}
    \    Failing UK    ${num}
    Fail    Not executed

For In User Keywords
    For In UK
    For In UK with Args    one    two    three    four

Nested For In User Keywords
    [Documentation]    FAIL    This ought to be enough
    Nested for In UK    foo    bar

For In Test And User Keywords
    [Documentation]    FAIL    This ought to be enough
    @{list} =    Create List    one    two
    : FOR    ${item}    IN    @{list}
    \    For In UK
    \    For In UK with Args    @{list}
    \    Nested For In UK    @{list}
    Fail    Not executed

For Variable Scope
    Variable Should Not Exist    ${var}
    : FOR    ${var}    IN    @{NUMS}
    \    Log    ${var}
    Should Be Equal    ${var}    5
    : FOR    ${var}    IN    foo
    \    Log    ${var}
    Should Be Equal    ${var}    foo

For With Assign
    : FOR    ${x}    IN    y    z
    \    ${v1} =    Set Variable    value 1
    \    ${v2}    ${v3} =    Create List    value 2    value 3
    \    @{list} =    Create List    ${1}    ${2}    ${3}    ${x}
    Should Be Equal    ${v1}    value 1
    Should Be Equal    ${v2}    value 2
    Should Be Equal    ${v3}    value 3
    Should Be True    @{list} == [1, 2, 3, 'z']

For With Invalid Assign
    [Documentation]    FAIL     Cannot set variables: Expected list-like value, got string.
    : FOR    ${i}    IN    1    2    3
    \    ${x}    ${y} =    Set Variable    Only one value
    \    Fail    Not executed
    Fail    Not executed

For Without In 1
    [Documentation]    FAIL    ${NO VALUES}
    Log    This is executed
    : FOR    ${var}    IN
    \    Fail    Not Executed
    Fail    Not Executed

For Without In 2
    [Documentation]    FAIL     Invalid FOR loop variable '\@{NUMS}'.
    Log    This is executed
    : FOR    ${var}    @{NUMS}    IN
    \    Fail    Not Executed
    Fail    Not Executed

For Without In 3
    [Documentation]    FAIL     Invalid FOR loop variable 'one'.
    Log    This is executed
    : FOR    ${var}    one    two    three    IN
    \    Fail    Not Executed
    Fail    Not Executed

For Without Parameters
    [Documentation]    FAIL    ${NO VARIABLES}
    Log    This is executed
    : FOR
    \   Fail    Not Executed
    Fail    Not Executed

For Without Variable
    [Documentation]    FAIL    ${NO VARIABLES}
    Log    This is executed
    : FOR    IN    one    two
    \    Fail    Not Executed
    Fail    Not Executed

Variable Format 1
    [Documentation]    FAIL    Invalid FOR loop variable 'var'.
    Log    This is executed
    : FOR    var    IN    one    two
    \    Fail    Not Executed
    Fail    Not Executed

Variable Format 2
    [Documentation]    FAIL    Invalid FOR loop variable '$var'.
    Log    This is executed
    : FOR    $var    IN    one    two
    \    Fail    Not Executed
    Fail    Not Executed

Variable Format 3
    [Documentation]    FAIL    Invalid FOR loop variable '@{var}'.
    Log    This is executed
    : FOR    @{var}    IN    one    two
    \    Fail    Not Executed
    Fail    Not Executed

Variable Format 4
    [Documentation]    FAIL    Invalid FOR loop variable 'notvar'.
    Log    This is executed
    : FOR    ${var}    ${var2}    notvar    IN    one    two
    ...    three
    \    Fail    Not Executed
    Fail    Not Executed

For With Non Existing Keyword
    [Documentation]    FAIL     No keyword with name 'Non Existing' found.
    : FOR    ${i}    IN    1    2    3
    \    Non Existing
    Fail    Not Executed

For With Non Existing Variable
    [Documentation]    FAIL     Variable '\${nonexisting}' not found.
    : FOR    ${i}    IN    1    2    3
    \    Log    ${nonexisting}
    Fail    Not Executed

For With Multiple Variables
    : FOR    ${x}    ${y}    IN
    ...      1       a
    ...      2       b
    ...      3       c
    ...      4       d
    \    Log    ${x}${y}
    Should Be Equal    ${x}${y}    4d
    : FOR    ${a}    ${b}    ${c}    ${d}    ${e}    IN
    ...    @{NUMS}    @{NUMS}
    \    Should Be Equal    ${a}${b}${c}${d}${e}    12345
    Should Be Equal    ${a}${b}${c}${d}${e}    12345

For With Non-Matching Number Of Parameters And Variables 1
    [Documentation]    FAIL     ${WRONG VALUES} Got 3 variables but 5 values.
    Log    This is executed
    : FOR    ${a}    ${b}    ${c}    IN    @{NUMS}
    \    Fail    Not executed
    Fail    Not executed

For With Non-Matching Number Of Parameters And Variables 2
    [Documentation]    FAIL     ${WRONG VALUES} Got 4 variables but 3 values.
    Log    This is executed
    : FOR    ${a}    ${b}    ${c}    ${d}    IN    a     b    c
    \    Fail    Not executed
    Fail    Not executed

Cut Long Variable Value In For Item Name
    ${v10} =    Set Variable    0123456789
    ${v100} =    Evaluate    '${v10}' * 10
    ${v200} =    Evaluate    '${v100}' * 2
    ${v201} =    Set Variable    ${v200}1
    ${v300} =    Evaluate    '${v100}' * 3
    ${v10000} =    Evaluate    '${v100}' * 100
    : FOR    ${var}    IN    ${v10}    ${v100}    ${v200}    ${v201}
    ...    ${v300}    ${v10000}
    \    Log    ${var}
    : FOR    ${var1}    ${var2}    ${var3}    IN    ${v10}    ${v100}
    ...    ${v200}    ${v201}    ${v300}    ${v10000}
    \    Log Many    ${var1}    ${var2}    ${var3}
    Should Be Equal    ${var}    ${var3}    Sanity check

For with illegal xml characters
    : FOR    ${var}    IN    @{ILLEGAL VALUES}
    \    Log    ${var}

For In Range
    : FOR    ${i}    IN RANGE    100
    \    @{result} =    Create List    @{result}    ${i}
    \    Log    i: ${i}
    Should Be True    @{result} == list(range(100))

For In Range With Start And Stop
    : FOR    ${item}    IN RANGE    1    5
    \    @{result} =    Create List    @{result}    ${item}
    Should Be True    @{result} == [1, 2, 3,4]

For In Range With Start, Stop And Step
    : FOR    ${item}    IN RANGE    10    2    -3
    \    @{result} =    Create List    @{result}    ${item}
    Should Be True    @{result} == [10, 7, 4]

For In Range With Float Stop 1
    : FOR    ${item}    IN RANGE    3.14
    \    @{result} =    Create List    @{result}    ${item}
    Should Be True    @{result} == [0, 1, 2, 3]

For In Range With Float Stop 2
    : FOR    ${item}    IN RANGE    3.0
    \    @{result} =    Create List    @{result}    ${item}
    Should Be True    @{result} == [0, 1, 2]

For In Range With Float Start And Stop 1
    : FOR    ${item}    IN RANGE    -1.5    1.5
    \    @{result} =    Create List    @{result}    ${item}
    Should Be True    @{result} == [-1.5, -0.5, 0.5]

For In Range With Float Start And Stop 2
    : FOR    ${item}    IN RANGE    -1.5    1.500001
    \    @{result} =    Create List    @{result}    ${item}
    Should Be True    @{result} == [-1.5, -0.5, 0.5, 1.5]

For In Range With Float Start, Stop And Step
    : FOR    ${item}    IN RANGE    10.99    2.11    -3.04
    \    @{result} =    Create List    @{result}    ${item}
    Should Be True    @{result} == [10.99, 7.95, 4.91]

For In Range With Variables In Arguments
    : FOR    ${i}    IN RANGE    ${1}    ${3}
    \    @{result} =    Create List    @{result}    ${i}
    Should Be True    @{result} == [1, 2]
    : FOR    ${j}    IN RANGE    @{result}
    \    Should Be Equal    ${j}    ${1}

For In Range With Expressions
    : FOR    ${i}    IN RANGE    ${3}-2    (3+${6})/3
    \    @{result} =    Create List    @{result}    ${i}
    Should Be True    @{result} == [1,2]

For In Range With Expressions Containing Floats
    : FOR    ${i}    IN RANGE    3 + 0.14    1.5 - 2.5    2 * -1
    \    @{result} =    Create List    @{result}    ${i}
    Should Be True    @{result} == [3.14, 1.14, -0.86]

For In Range With Multiple Variables
    : FOR    ${i}    ${j}    ${k}    IN RANGE    -1    11
    \    @{result} =    Create List    @{result}    ${i}-${j}-${k}
    Should Be True    @{result} == ['-1-0-1', '2-3-4', '5-6-7', '8-9-10']

For In Range With Too Many Arguments
    [Documentation]    FAIL    FOR IN RANGE expected 1-3 arguments, got 4.
    : FOR    ${i}    IN RANGE    1    2    3    4
    \    Fail    Not executed
    Fail    Not executed

For In Range With No Arguments
    [Documentation]    FAIL    ${NO VALUES}
    : FOR    ${i}    IN RANGE
    \    Fail    Not executed
    Fail    Not executed

For In Range With Non-Number Arguments 1
    [Documentation]    FAIL    STARTS: Converting argument of FOR IN RANGE failed: SyntaxError:
    : FOR    ${i}    IN RANGE    not a number
    \    Fail    Not executed
    Fail    Not executed

For In Range With Non-Number Arguments 2
    [Documentation]    FAIL    STARTS: Converting argument of FOR IN RANGE failed: TypeError:
    : FOR    ${i}    IN RANGE    0     ${NONE}
    \    Fail    Not executed
    Fail    Not executed

For In Range With Wrong Number Of Variables
    [Documentation]    FAIL    ${WRONG VALUES} Got 2 variables but 11 values.
    : FOR    ${x}    ${y}    IN RANGE    11
    \    Fail    Not executed
    Fail    Not executed

For In Range With Non-Existing Variables In Arguments
    [Documentation]    FAIL    Variable '\@{non existing}' not found.
    : FOR    ${i}    IN RANGE    @{non existing}
    \    Fail    Not executed
    Fail    Not executed

For loops are case and space insensitive
    : f o r  ${x}  i n  a  b  c
    \    @{result} =    Create List    @{result}    ${x}
    Should Be True    @{result} == ['a', 'b', 'c']
    : F o R  ${X X}  i n r a n g e  1  2
    \    @{result} =    Create List    @{result}    ${X X}
    Should Be True    @{result} == ['a', 'b', 'c', 1]
    :for           ${i}              inrange           2              4
    \    @{result} =    Create List    @{result}    ${i}
    Should Be True    @{result} == ['a', 'b', 'c', 1, 2, 3]

For word can have many colons
    ::::::::FOR    ${i}    IN    0    1    2
    \    @{result} =    Create List    @{result}    ${i}
    Should Be True    @{result} == ['0', '1', '2']
    :::f:o:r:::    ${i}    inrange    3    6
    \    @{result} =    Create List    @{result}    ${i}
    Should Be True    @{result} == ['0', '1', '2', 3, 4, 5]

*** Keywords ***
My UK
    No Operation
    Log    We are in My UK

My UK 2
    [Arguments]    ${arg}
    My UK
    Log    My UK 2 got argument "${arg}"
    My UK

Failing UK
    [Arguments]    ${num}
    My UK 2    ${num}
    Should Not Be Equal    ${num}    2    Failure with ${num}    no values

For In UK
    Log    Not for yet
    : FOR    ${x}    IN    1    2
    \    Log    This is for with ${x}
    \    My UK
    Log    Not for anymore

For In UK With Args
    [Arguments]    @{args}
    : FOR    ${arg}    IN    @{args}
    \    My UK 2    ${arg}
    Should Be Equal    ${arg}    @{args}[-1]
    : FOR    ${arg}    IN    only once
    \    Log    This for loop is executed ${arg}
    Should Be Equal    ${arg}    only once

Nested For In UK
    [Arguments]    @{args}
    : FOR    ${arg}    IN    @{args}
    \    For In UK
    \    Nested for In UK 2    @{args}

Nested For In UK 2
    [Arguments]    @{args}
    : FOR    ${arg}    IN    @{args}
    \    For In UK
    \    Log    Got arg: ${arg}
    Fail    This ought to be enough

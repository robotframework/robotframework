*** Settings ***
Documentation  NO RIDE because we want to test different formatting
Variables   binary_list.py

*** Variables ***
@{NUMS}  1  2  3  4  5
@{EMPTY_LIST}
${NO VALUES}  FAIL FOR loop has no loop values.
${NO KEYWORDS}  FAIL FOR loop contains no keywords.
${NO VARIABLES}  FAIL FOR loop has no loop variables.

*** Test Cases ***
Simple For
    Log  Not yet in For
    :FOR  ${var}  IN  one  two
    \  Log  var: ${var}
    Log  Not in For anymore

Simple For 2
    :FOR  ${num}  IN  @{NUMS}  6
    \  Log  ${num}
    \  Log  Hello from for loop
    \  No Operation
    \  Run Keyword If    ${num} in [2,6]    Log    Presidential Candidate!   WARN

Empty For
    [Documentation]  ${NO KEYWORDS}
    :FOR  ${var}  IN  one  two
    Fail  Should not executed

For Without Value
    [Documentation]  ${NO VALUES}
    :FOR  ${var}  IN
    \  Fail  not executed

For Loop Over Empty List Var
    :FOR  ${var}  IN  @{EMPTY_LIST}
    \  Fail  not executed
    Fail if variable exists  $var

For Failing
    [Documentation]  FAIL Here we fail!
    :FOR  ${num}  IN  @{NUMS}
    \  Log  Hello before failing kw
    \  Fail  Here we fail!
    \  Log  Hello after failed kw

For Failing 2
    [Documentation]  FAIL Failure with 4
    :FOR  ${num}  IN  @{NUMS}
    \  Log  Before Check
    \  Should Not Be True  ${num} == 4  Failure with ${num}
    \  Log  After Check

For With User Keywords
    [Documentation]  FAIL Fail outside for
    :FOR  ${x}  IN  foo  bar
    \  My UK
    \  My UK 2  ${x}
    Fail  Fail outside for

For With Failures In User Keywords
    [Documentation]  FAIL Failure with 2
    :FOR  ${num}  IN  @{NUMS}
    \  Failing UK  ${num}

Many Fors In One Test
    :FOR  ${x}  IN  foo  bar
    \  Log  In first for with var "${x}"
    :FOR  ${y}  IN  Hello, world!
    \  My UK 2  ${y}
    Log  Outside for loop
    :FOR  ${z}  IN  a  b
    \  Log  Third for loop
    \  Noop
    \  Log  Value: ${z}
    Log  End of the test

For With Values In Multiple Rows
    :FOR  ${i}  IN  @{nums}  6  7  8  9
    ...  10
    \  Log  ${i}
    Equals  ${i}  10

For With Keyword Args On Multiple Rows
    :FOR  ${var}  IN  one  two
    \  ${msg} =  Catenate  1  2  3  4  5
    ...  6  7  ${var}
    \  Log  ${msg}
    \  Equals  ${msg}  1 2 3 4 5 6 7 ${var}

For In User Keywords
    For In UK
    For In UK with Args  one  two  three  four

Nested For In User Keywords
    [Documentation]  FAIL This ought to be enough
    Nested for In UK  foo  bar

For In Test And User Keywords
    [Documentation]  FAIL This ought to be enough
    @{list} =  List  one  two
    :FOR  ${item}  IN  @{list}
    \  For In UK
    \  For In UK with Args  @{list}
    \  Nested For In UK  @{list}

For Variable Scope
    Fail if variable exists  $var
    :FOR  ${var}  IN  @{NUMS}
    \  Log  ${var}
    Equals  ${var}  5
    :FOR  ${var}  IN  foo
    \  Log  ${var}
    Equals  ${var}  foo

For With Set
    :FOR  ${x}  IN  y  z
    \  ${v1} =  Set  value 1
    \  ${v2}  ${v3} =  Create List  value 2  value 3
    \  @{list} =  Create List  ${1}  ${2}  ${3}  ${x}
    Equals  ${v1}  value 1
    Equals  ${v2}  value 2
    Equals  ${v3}  value 3
    Fail Unless  @{list} == [1, 2, 3, 'z']

For Without In 1
    [Documentation]  ${NO VALUES}
    Log  This is executed
    : FOR  ${var}
    \   Fail  Not Executed

For Without In 2
    [Documentation]  FAIL Invalid FOR loop variable '\@{NUMS}'.
    Log  This is executed
    : FOR  ${var}  @{NUMS}
    \   Fail  Not Executed

For Without In 3
    [Documentation]  FAIL Invalid FOR loop variable 'one'.
    Log  This is executed
    : FOR  ${var}  one  two  three
    \   Fail  Not Executed

For Without Parameters
    [Documentation]  ${NO VARIABLES}
    Log  This is executed
    : FOR
    \   Fail  Not Executed

For Without Variable
    [Documentation]  ${NO VARIABLES}
    Log  This is executed
    : FOR  IN  one  two
    \   Fail  Not Executed

Variable Format 1
    [Documentation]  FAIL Invalid FOR loop variable 'var'.
    Log  This is executed
    : FOR  var  IN  one  two
    \   Fail  Not Executed

Variable Format 2
    [Documentation]  FAIL Invalid FOR loop variable '$var'.
    Log  This is executed
    : FOR  $var  IN  one  two
    \   Fail  Not Executed

Variable Format 3
    [Documentation]  FAIL Invalid FOR loop variable '@{var}'.
    Log  This is executed
    : FOR  @{var}  IN  one  two
    \   Fail  Not Executed

Variable Format 4
    [Documentation]  FAIL Invalid FOR loop variable 'notvar'.
    Log  This is executed
    : FOR  ${var}  ${var2}  notvar  IN  one  two  three
    \   Fail  Not Executed

For With Non Existing Keyword
    [Documentation]  FAIL No keyword with name 'Non Existing' found.
    :FOR  ${i}  IN  1  3
    \  Non Existing

For With Non Existing Variable
    [Documentation]  FAIL Variable '\${nonexisting}' not found.
    :FOR  ${i}  IN  1  3
    \  Log  ${nonexisting}

For With Invalid Set
    [Documentation]  FAIL Cannot assign return values: Expected list-like object, got string instead.
    :FOR  ${i}  IN  1  3
    \  ${x}  ${y} =  Set Variable  Only one value

For With Multiple Variables
    :FOR  ${x}  ${y}  IN  1  a  2  b
    ...  3  c  4  d
    \  Log  ${x}${y}
    Equals  ${x}${y}  4d
    :FOR  ${a}  ${b}  ${c}  ${d}  ${e}  IN  @{NUMS}
    ...  @{NUMS}
    \  Equals  ${a}${b}${c}${d}${e}  12345
    Equals  ${a}${b}${c}${d}${e}  12345

For With Wrong Number Of Parameters For Multiple Variables
    [Documentation]  FAIL Number of FOR loop values should be multiple of variables. Got 3 variables but 5 values.
    Log  This is executed
    :FOR  ${a}  ${b}  ${c}  IN  @{NUMS}
    \  Fail  Not executed

Cut Long Variable Value In For Item Name
    ${v10} =  Set  0123456789
    ${v100} =  Evaluate  "${v10}" * 10
    ${v200} =  Evaluate  "${v100}" * 2
    ${v201} =  Set  ${v200}1
    ${v300} =  Evaluate  "${v100}" * 3
    ${v10000} =  Evaluate  "${v100}" * 100
    :FOR  ${var}  IN  ${v10}  ${v100}  ${v200}  ${v201}  ${v300}
    ...  ${v10000}
    \  Log  ${var}
    :FOR  ${var1}  ${var2}  ${var3}  IN  ${v10}  ${v100}  ${v200}
    ...  ${v201}  ${v300}  ${v10000}
    \  Log Many  ${var1}  ${var2}  ${var3}
    Equals  ${var}  ${var3}  Sanity check

For with illegal xml characters
    :FOR    ${var}  IN  @{ILLEGAL VALUES}
    \       Log     ${var}

For In Range
    @{var} =  List
    :FOR  ${i}  IN RANGE  100
    \  @{var} =  List  @{var}  ${i}
    \  Log  i: ${i}
    Fail Unless  @{var} == range(100)

For In Range With Start And Stop
    @{var} =  List
    :FOR  ${i}  IN RANGE  1  5
    \  @{var} =  List  @{var}  ${i}
    Fail Unless  @{var} == [1, 2, 3,4]

For In Range With Start, Stop And Step
    @{var} =  List
    :FOR  ${myvar}  IN RANGE  10  2  -3
    \  @{var} =  List  @{var}  ${myvar}
    Fail Unless  @{var} == [10, 7, 4]

For In Range With Variables In Arguments
    @{var} =  List
    :FOR  ${i}  IN RANGE  ${1}  ${3}
    \  @{var} =  List  @{var}  ${i}
    Fail Unless  @{var} == [1,2]
    :FOR  ${j}  IN RANGE  @{var}
    \  Equals  ${j}  ${1}

For In Range With Expressions in Arguments
    @{var} =  List
    :FOR  ${i}  IN RANGE  ${3}-2  (3+${6})/3
    \  @{var} =  List  @{var}  ${i}
    Fail Unless  @{var} == [1,2]

For In Range With Multiple Variables
    @{var} =  List
    :FOR  ${i}  ${j}  ${k}  IN RANGE  -1  11
    \  @{var} =  List  @{var}  ${i}-${j}-${k}
    Fail Unless  @{var} == ['-1-0-1', '2-3-4', '5-6-7', '8-9-10']

For In Range With Too Many Arguments
    [Documentation]  FAIL FOR IN RANGE expected 1-3 arguments, got 4 instead.
    :FOR  ${i}  IN RANGE  1  2  3  4
    \  Fail  Not executed

For In Range With No Arguments
    [Documentation]  ${NO VALUES}
    :FOR  ${i}  IN RANGE
    \  Fail  Not executed

For In Range With Non Number Arguments
    [Documentation]  FAIL STARTS: Converting argument of FOR IN RANGE failed: SyntaxError:
    :FOR  ${i}  IN RANGE  not a number
    \  Fail  Not executed

For In Range With Wrong Number Of Variables
    [Documentation]  FAIL Number of FOR loop values should be multiple of variables. Got 2 variables but 11 values.
    :FOR  ${x}  ${y}  IN RANGE  11
    \  Fail  Not executed

For In Range With Non-Existing Variables In Arguments
    [Documentation]  FAIL Variable '\@{non existing}' not found.
    :FOR  ${i}  IN RANGE  @{non existing}
    \  Fail  Not executed

For In Range With None As Range
    [Documentation]  FAIL STARTS: Converting argument of FOR IN RANGE failed: TypeError:
    :FOR  ${i}  IN RANGE  ${NONE}
    \  Fail  Not executed

For loops are case and space insensitive
    ${result} =  Set Variable  ${EMPTY}
    : f o r  ${c}  i n  a  b  c
    \  ${result} =  Set Variable  ${result}${c}
    : F o R  ${i}  i n r a n g e  1  2
    \  ${result} =  Set Variable  ${result}${i}
    :for  ${i}  inrange  2  4
    \  ${result} =  Set Variable  ${result}${i}
    Should Be Equal  ${result}  abc123

For word can have many colons
    ${result} =  Set Variable  ${EMPTY}
    ::::::::FOR  ${i}  IN  0  1  2  3
    \  ${result} =  Set Variable  ${result}${i}
    :::f:o:r:::  ${i}  inrange  4  10
    \  ${result} =  Set Variable  ${result}${i}
    Should Be Equal  ${result}  0123456789

For In Range With Float Start, Stop And Step
    @{var} =  List
    :FOR  ${myvar}  IN RANGE  10.99  2.11  -3.04
    \  @{var} =  List  @{var}  ${myvar}
    Fail Unless  @{var} == [10.99, 7.95, 4.91]

*** Keywords ***
My UK
    No Operation
    Log  We are in My UK

My UK 2
    [Arguments]  ${arg}
    My UK
    Log  My UK 2 got argument "${arg}"
    My UK

Failing UK
    [Arguments]  ${num}
    My UK 2  ${num}
    Fail If  ${num} == 2  Failure with ${num}

For In UK
    Log  Not for yet
    :FOR  ${x}  IN  1  2
    \  Log  This is for with ${x}
    \  My UK
    Log  Not for anymore

For In UK With Args
    [Arguments]  @{args}
    :FOR  ${arg}  IN  @{args}
    \  My UK 2  ${arg}
    :FOR  ${arg}  IN  only once
    \  Log  This for loop is executed ${arg}
    Equals  ${arg}  only once

Nested For In UK
    [Arguments]  @{args}
    :FOR  ${arg}  IN  @{args}
    \  For In UK
    \  Nested for In UK 2  @{args}

Nested For In UK 2
    [Arguments]  @{args}
    :FOR  ${arg}  IN  @{args}
    \  For In UK
    \  Log  Got arg: ${arg}
    Fail  This ought to be enough


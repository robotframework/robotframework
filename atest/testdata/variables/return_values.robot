*** Settings ***
Documentation     NO RIDE because it would sanitize formatting too much.
Library           ExampleLibrary
Library           Collections
Library           get_file_lib.py

*** Variables ***
&{DICT}           foo=bar    muu=mi

*** Test Cases ***
Simple Scalar Variable
    ${setvar} =    Set Variable    this value is set
    Should Be Equal    ${setvar}    this value is set

Empty Scalar Variable
    ${setvar} =    Set Variable    ${EMPTY}
    Should Be Equal    ${setvar}    ${EMPTY}

List To Scalar Variable
    ${setvar} =    Create List    a    ${2}
    Should Be Equal    ${setvar[0]}    a
    Should Be Equal    ${setvar[1]}    ${2}

Python Object To Scalar Variable
    ${var} =    Return Object    This is my name
    Should Be Equal    ${var.name}    This is my name

Unrepresentable object to scalar variable
    ${var} =    Return Unrepresentable Objects    identifier=xxx    just_one=True
    Should Be Equal    ${var.identifier}    xxx

None To Scalar Variable
    ${var} =    Evaluate    None
    Should Be True    ${var} is None
    Should Not Be Equal    ${var}    None

Multible Scalar Variables
    ${var1}    ${var2} =    Create List    one    ${2}
    Should Be Equal    ${var1}    one
    Should Be Equal    ${var2}    ${2}
    ${a}    ${b}    ${c}    ${d}    ${e}    ${f}    ${g} =    Evaluate    list('abcdefg')
    Should Be Equal    ${a}-${b}-${c}-${d}-${e}-${f}-${g}    a-b-c-d-e-f-g

Unrepresentable objects to scalar variables
    ${o1}    ${o2} =    Return Unrepresentable Objects    identifier=123
    Should Be Equal    ${o1.identifier}    123
    Should Be Equal    ${o2.identifier}    123

None To Multiple Scalar Variables
    ${x}    ${y} =    Run Keyword If    False    Not Executed
    Should Be Equal    ${x}    ${None}
    Should Be Equal    ${y}    ${None}

Multiple Scalars With Too Few Values
    [Documentation]    FAIL Cannot set variables: Expected 3 return values, got 2.
    ${a}    ${b}    ${c} =    Create List    a    b

Multiple Scalars With Too Many Values
    [Documentation]    FAIL Cannot set variables: Expected 3 return values, got 4.
    ${a}    ${b}    ${c} =    Create List    a    b    c    ${4}

Multiple Scalars When No List Returned 1
    [Documentation]    FAIL Cannot set variables: Expected list-like value, got string.
    ${a}    ${b} =    Set Variable    This is not list

Multiple Scalars When No List Returned 2
    [Documentation]    FAIL Cannot set variables: Expected list-like value, got integer.
    ${a}    ${b} =    Set Variable    ${42}

List Variable
    @{listvar} =    Create List    h    e    ll    o
    Should Be Equal    ${listvar}[0]    h
    Should Be Equal    ${listvar}[1]    e
    Should Be Equal    ${listvar}[2]    ll
    Should Be Equal    ${listvar}[3]    o
    @{list} =    Create List
    Should Be Empty    ${list}

List Variable From Consumable Iterable
    @{listvar} =    Return Consumable Iterable    Keijo    Mela
    Should Be Equal    ${listvar}[0]    Keijo
    Should Be Equal    ${listvar}[1]    Mela
    Length Should Be    ${listvar}    2

List Variable From List Subclass
    @{listvar} =    Return List Subclass    Keijo    Mela
    Should Be Equal    ${listvar}[0]    Keijo
    Should Be Equal    ${listvar}[1]    Mela

List Variable From Dictionary
    @{list} =    Create Dictionary    name=value
    Should Be Equal    @{list}    name
    Should Be True    ${list} == ['name']
    @{list} =    Create Dictionary    a=1    b=2    c=3
    Should Be True    set(${list}) == {'a', 'b', 'c'}

Unrepresentable objects to list variables
    @{unrepr} =    Return Unrepresentable Objects    identifier=list
    Length Should Be    ${unrepr}    2
    FOR    ${obj}    IN    @{unrepr}
        Should Be Equal    ${obj.identifier}    list
        ${var} =    Set Variable    ${obj}
        Should Be Equal    ${var}    ${obj}
    END

None To List Variable
    @{list} =    Log    This returns None
    Should Be True    ${list} == []

List When Non-List Returned 1
    [Documentation]    FAIL Cannot set variable '\@{list}': Expected list-like value, got string.
    @{list} =    Set Variable    kekkonen

List When Non-List Returned 2
    [Documentation]    FAIL Cannot set variable '\@{list}': Expected list-like value, got integer.
    @{list} =    Set Variable    ${42}

Only One List Variable Allowed 1
    [Documentation]    FAIL Assignment can contain only one list variable.
    @{list}    @{list2} =    Fail    Not executed

Only One List Variable Allowed 2
    [Documentation]    FAIL Assignment can contain only one list variable.
    @{list}    ${scalar}    @{list2} =    Fail    Not executed

List After Scalars
    ${first}    @{rest} =    Evaluate    range(5)
    Should Be Equal    ${first}    ${0}
    Should Be True    @{rest} == [1, 2, 3, 4]
    ${a}    ${b}    @{c} =    Create List    1    2    c    d    e    f
    Should Be Equal   ${a}-${b}    1-2
    Should Be True    @{c} == ['c', 'd', 'e', 'f']
    ${a}    ${b}    @{c} =    Create List    1    2
    Should Be Equal   ${a}-${b}-@{c}    1-2-[]

List Before Scalars
    @{list}    ${scalar} =    Set Variable    ${1}    2
    Should be equal      @{list}-${scalar}     [1]-2
    @{list}    ${x}    ${y}    ${z} =    Set Variable    ${1}    ${2}    x    y    z
    Should be equal      @{list}-${x}-${y}-${z}     [1, 2]-x-y-z
    @{list}    ${x}    ${y}    ${z} =    Set Variable    x    y    z
    Should be equal      @{list}-${x}-${y}-${z}     []-x-y-z

List Between Scalars
    ${first}    @{list}    ${last} =    Set Variable    1    2    3    4
    Should be equal      ${first}    1
    Should be true       ${list} == ['2', '3']
    Should be equal      ${last}    4
    ${first}    ${second}   @{list}    ${last} =    Set Variable    1    2    3
    Should be equal      ${first}     1
    Should be equal      ${second}    2
    Should be true       ${list} == []
    Should be equal      ${last}    3

None To Scalar Variables And List Variable
    ${a}    ${b}    ${c}    @{d} =    No Operation
    Should Be Equal    ${a}    ${None}
    Should Be Equal    ${b}    ${None}
    Should Be Equal    ${c}    ${None}
    Should Be True    ${d} == []
    @{list}    ${scalar} =    No Operation
    Should Be Equal    ${list}-${scalar}    []-None
    ${first}    @{rest}    ${last} =    No Operation
    Should Be Equal    ${first}-${rest}-${last}    None-[]-None

List and scalars with not enough values 1
    [Documentation]     FAIL Cannot set variables: Expected 2 or more return values, got 1.
    ${first}    ${second}    @{list} =    Create List    1

List and scalars with not enough values 2
    [Documentation]     FAIL Cannot set variables: Expected 2 or more return values, got 1.
    ${first}    @{list}    ${last} =    Create List    1

List and scalars with not enough values 3
    [Documentation]     FAIL Cannot set variables: Expected 1 or more return values, got 0.
    @{list}    ${last} =    Create List

Dictionary return value
    &{ret} =     Create dictionary    foo=bar   muu=mi
    Dictionaries Should Be Equal    ${ret}    ${DICT}

None To Dict
    &{ret} =    No Operation
    Should Be True    &{ret} == {}

Dictionary is dot-accessible
    &{dict} =    Evaluate    {'key': 'value'}
    Should Be Equal    ${dict.key}    value
    &{nested} =    Evaluate    collections.OrderedDict([('key', 'value'), ('nested', {'key': 'nested value'})])    modules=collections
    Should Be Equal    ${nested.key}    value
    Should Be Equal    ${nested.nested.key}    nested value

Scalar dictionary is not dot-accessible
    [Documentation]     FAIL STARTS: Resolving variable '${normal.key}' failed: AttributeError:
    ${normal} =    Evaluate    {'key': 'value'}
    Should Be Equal    ${normal['key']}    value
    Should Be Equal    ${normal.key}    value

Dictionary only allowed alone 1
    [Documentation]     FAIL Dictionary variable cannot be assigned with other variables.
    ${s}    &{d} =    Fail    Not executed

Dictionary only allowed alone 2
    [Documentation]     FAIL Dictionary variable cannot be assigned with other variables.
    &{d}    ${s} =    Fail    Not executed

Dictionary only allowed alone 3
    [Documentation]     FAIL Dictionary variable cannot be assigned with other variables.
    &{d}    @{l} =    Fail    Not executed

Dictionary only allowed alone 4
    [Documentation]     FAIL Dictionary variable cannot be assigned with other variables.
    @{l}    &{d} =    Fail    Not executed

Dictionary only allowed alone 5
    [Documentation]     FAIL Dictionary variable cannot be assigned with other variables.
    &{d1}    &{d2} =    Fail    Not executed

Dict when non-dict returned 1
    [Documentation]    FAIL Cannot set variable '\&{ret}': Expected dictionary-like value, got list.
    &{ret} =     Create List

Dict when non-dict returned 2
    [Documentation]    FAIL Cannot set variable '\&{ret}': Expected dictionary-like value, got string.
    &{ret} =     Set variable   foo

Dict when non-dict returned 3
    [Documentation]    FAIL Cannot set variable '\&{ret}': Expected dictionary-like value, got integer.
    &{ret} =     Set variable    ${5}

Long String To Scalar Variable
    ${v300} =    Evaluate    '123456789 ' * 30
    Length Should Be    ${v300}    300

Long Values To List Variable
    ${v99} =    Evaluate    ('123456789 ' * 10).strip()
    @{long} =    Create List    ${v99}    ${v99}    ${v99}
    Should Be Equal    ${long}[0]    ${v99}
    Should Be Equal    ${long}[1]    ${v99}
    Should Be Equal    ${long}[2]    ${v99}

Big Items In Dictionary
    ${v100} =    Evaluate    '1234567890' * 10
    &{big} =    Create Dictionary    _${v100}=${v100}    second=${v100}
    Should Be Equal    ${big._${v100}}    ${v100}
    Should Be Equal    ${big.second}    ${v100}

No Keyword
    [Documentation]    FAIL Keyword name cannot be empty.
    ${nokeyword}

Failing Keyword
    [Documentation]    FAIL Failing instead of returning
    ${ret} =    Fail    Failing instead of returning

Failing Keyword And Teardown
    [Documentation]    FAIL Failing, again, instead of returning.
    ...
    ...                Also teardown failed:
    ...                Teardown is executed normally. But fails...
    ${ret} =    Fail    Failing, again, instead of returning.
    [Teardown]    Fail    Teardown is executed normally. But fails...

Assign Mark Without Space
    ${var}=    Set Variable    hello
    Should Be Equal    ${var}    hello
    ${v1}    ${v2}=    Set Variable    hi    you
    Should Be Equal    ${v1}    hi
    Should Be Equal    ${v2}    you
    @{list}=    Set Variable    a    b    c
    Should Be Equal    ${list}[0] ${list}[1] ${list}[2]    a b c

No Assign Mark
    ${var}    Set Variable    hello
    Should Be Equal    ${var}    hello
    ${v1}    ${v2}    Set Variable    hi    you
    Should Be Equal    ${v1}    hi
    Should Be Equal    ${v2}    you
    @{list}    Set Variable    a    b    c
    Should Be Equal    ${list}[0] ${list}[1] ${list}[2]    a b c

Optional Assign Mark With Multiple Variables
    ${a}    ${b} =    Set Variable    a    b
    Should Be Equal    ${a}-${b}    a-b
    ${a}    ${b}    @{c}=    Set Variable    a    b    c
    Should Be Equal    ${a}-${b}    a-b
    Should Be Equal    @{c}    c

Assign Mark Can Be Used Only With The Last Variable
    [Documentation]    FAIL Assign mark '=' can be used only with the last variable.
    ${v1} =    ${v2} =    Set Variable    a    b

Files are not lists
    [Documentation]    FAIL Cannot set variable '\@{works not}': Expected list-like value, got file.
    ${works} =    Get open file
    @{works not} =    Get open file

Invalid count error is catchable
    [Documentation]    FAIL
    ...    Teardown failed:
    ...    Several failures occurred:
    ...
    ...    1) Cannot set variables: Expected 2 return values, got 3.
    ...
    ...    2) Also this is executed!
    Run Keyword And Expect Error
    ...    Cannot set variables: Expected 2 return values, got 3.
    ...    Assign multiple variables    too    many    args
    Run Keyword And Expect Error
    ...    Cannot set variables: Expected 1 or more return values, got 0.
    ...    Assign multiple variables
    [Teardown]    Run Keywords
    ...    Assign multiple variables    too    many    args    AND
    ...    Fail    Also this is executed!

Invalid type error is catchable
    [Documentation]    FAIL
    ...    Teardown failed:
    ...    Several failures occurred:
    ...
    ...    1) Cannot set variable '\@{x}': Expected list-like value, got boolean.
    ...
    ...    2) Cannot set variable '\&{x}': Expected dictionary-like value, got string.
    ...
    ...    3) Also this is executed!
    Run Keyword And Expect Error
    ...    Cannot set variable '\@{x}': Expected list-like value, got string.
    ...    Assign list variable    not list
    Run Keyword And Expect Error
    ...    Cannot set variable '\&{x}': Expected dictionary-like value, got integer.
    ...    Assign dict variable    ${42}
    [Teardown]    Run Keywords
    ...    Assign list variable    ${False}               AND
    ...    Assign dict variable    not dict               AND
    ...    Fail    Also this is executed!

*** Keywords ***
Assign multiple variables
     [Arguments]    @{args}
     ${x}    @{y} =    Create List    @{args}
     ${x}    ${y} =    Create List    @{args}

Assign list variable
     [Arguments]    ${arg}
     @{x} =    Set Variable    ${arg}

Assign dict variable
     [Arguments]    ${arg}
     &{x} =    Set Variable    ${arg}

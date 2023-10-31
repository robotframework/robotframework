*** Settings ***
Library           ExampleLibrary
Library           Collections
Library           get_file_lib.py
Variables         return_values.py

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
    [Documentation]    FAIL Setting variable '\@{list}' failed: Expected list-like value, got string.
    @{list} =    Set Variable    kekkonen

List When Non-List Returned 2
    [Documentation]    FAIL Setting variable '\@{list}' failed: Expected list-like value, got integer.
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
    [Documentation]     FAIL STARTS: Resolving variable '\${normal.key}' failed: AttributeError:
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
    [Documentation]    FAIL Setting variable '\&{ret}' failed: Expected dictionary-like value, got list.
    &{ret} =     Create List

Dict when non-dict returned 2
    [Documentation]    FAIL Setting variable '\&{ret}' failed: Expected dictionary-like value, got string.
    &{ret} =     Set variable   foo

Dict when non-dict returned 3
    [Documentation]    FAIL Setting variable '\&{ret}' failed: Expected dictionary-like value, got integer.
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

Non-existing keyword 1
    [Documentation]    FAIL No keyword with name 'I do not exist' found.
    ${x} =    I do not exist

Non-existing keyword 2
    [Documentation]    FAIL No keyword with name 'I do not exist either' found.
    ${x}      I do not exist either

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

Named based on another variable
    ${x} =    Set Variable    y
    ${${x}} =    Set Variable    z
    Should Be Equal    ${y}    z
    ${x-${x}-${y}} =    Set Variable    x-${x}-${y}
    Should Be Equal    ${x-y-z}    x-y-z

Non-existing variable in name
    [Documentation]    FAIL Setting variable '\${\${x}}' failed: Variable '\${x}' not found.
    ${${x}} =    Set Variable    z

Files are not lists
    [Documentation]    FAIL Setting variable '\@{works not}' failed: Expected list-like value, got file.
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
    ...    1) Setting variable '\@{x}' failed: Expected list-like value, got boolean.
    ...
    ...    2) Setting variable '\&{x}' failed: Expected dictionary-like value, got string.
    ...
    ...    3) Also this is executed!
    Run Keyword And Expect Error
    ...    Setting variable '\@{x}' failed: Expected list-like value, got string.
    ...    Assign list variable    not list
    Run Keyword And Expect Error
    ...    Setting variable '\&{x}' failed: Expected dictionary-like value, got integer.
    ...    Assign dict variable    ${42}
    [Teardown]    Run Keywords
    ...    Assign list variable    ${False}               AND
    ...    Assign dict variable    not dict               AND
    ...    Fail    Also this is executed!

Invalid assign
    [Documentation]    FAIL No keyword with name '\${oops' found.
    ${oops    Set Variable    whatever

Invalid assign with assign mark
    [Documentation]    FAIL No keyword with name '\${oops=' found.
    ${oops=    Set Variable    whatever

Too many assign marks
    [Documentation]    FAIL No keyword with name '\${oops}==' found.
    ${oops}==    Set Variable    whatever

Item assign to scalar dictionary
    ${dict_variable}=             Create Dictionary     key_str1=initial_value    ${0}=${99}

    ${dict_variable}[key_str1]=   Set Variable          replaced_value
    ${dict_variable}[${0}]=       Set Variable          ${100}
    ${dict_variable}[0]=          Set Variable          new_value

    ${tuple_as_key}=                     Evaluate       (1, 2, 3,)
    ${dict_variable}[${tuple_as_key}]=   Set Variable   tuple_value

    Should Be Equal    ${dict_variable}[key_str1]    replaced_value
    Should Be Equal    ${dict_variable}[${0}]        ${100}
    Should Be Equal    ${dict_variable}[0]           new_value

    Should Be Equal    ${dict_variable}[${tuple_as_key}]    tuple_value

Nested item assign
    ${dict_variable}=             Create Dictionary

    ${dict_variable}[list]=         Evaluate        [1, 2, 3]
    ${dict_variable}[list][0]=      Set Variable    ${101}
    ${dict_variable}[list][${1}]=   Set Variable    ${102}
    ${dict_variable}[list][-1]=     Set Variable    ${103}

    ${expected_list}=               Evaluate        [101, 102, 103]
    Should Be Equal                 ${dict_variable}[list]     ${expected_list}

    ${dict_variable}[dict]=         Evaluate        {"a": "b"}
    ${dict_variable}[dict][a]=      Set Variable    c
    ${dict_variable}[dict][${0}]=   Set Variable    zero_int
    ${dict_variable}[dict][0]=      Set Variable    zero_str

    ${expected_dict}=               Evaluate        {"a": "c", "0": "zero_str", 0: "zero_int"}
    Should Be Equal                 ${dict_variable}[dict]     ${expected_dict}

Item assign to scalar list
    ${list_variable}=       Create List    1    2    3

    ${list_variable}[0]=       Set Variable    100
    ${list_variable}[${1}]=    Set Variable    101
    ${list_variable}[-1]=      Set Variable    102

    Should Be Equal      ${list_variable}[0]    100
    Should Be Equal      ${list_variable}[1]    101
    Should Be Equal      ${list_variable}[2]    102
    Length Should Be     ${list_variable}       3

Slice assign to scalar list
    ${list_variable}=       Create List    1    2    3    4    5
    ${iterator1}=           Create List    101  102  103
    ${iterator2}=           Create List    104

    ${list_variable}[:2]=   Set Variable   ${iterator1}
    ${list_variable}[-2:]=  Set Variable   ${iterator2}

    Length Should Be     ${list_variable}       5
    Should Be Equal      ${list_variable}[0]    101
    Should Be Equal      ${list_variable}[1]    102
    Should Be Equal      ${list_variable}[2]    103
    Should Be Equal      ${list_variable}[3]    3
    Should Be Equal      ${list_variable}[4]    104

Item assign using variable as index
    ${int_variable}=        Set Variable   ${-1}
    ${str_variable}=        Set Variable   0
    ${slice_variable}=      Set Variable   ${{ slice(1, 2) }}
    ${strslice_variable}=   Set Variable   2:4

    ${list_variable}=       Create List    ${1}    ${2}    ${3}    ${4}    ${5}
    ${list_variable}[${int_variable}]
    ...  ${list_variable}[${str_variable}]
    ...  ${list_variable}[${slice_variable}]
    ...  ${list_variable}[${strslice_variable}]=   Evaluate    (105, 101, [102], [103, 104])

    ${expected_list}=    Create List         ${101}  ${102}  ${103}  ${104}  ${105}
    Should Be Equal      ${list_variable}    ${expected_list}

Item assign to object with setitem capability
    # Reset the object if used in other test
    Call Method    ${OBJECT_WITH_SETITEM_CAP}    clear

    ${OBJECT_WITH_SETITEM_CAP}[str_key]=    Set Variable    new_value
    ${OBJECT_WITH_SETITEM_CAP}[0]=          Set Variable    value_str
    ${OBJECT_WITH_SETITEM_CAP}[${0}]=       Set Variable    value_int
    ${OBJECT_WITH_SETITEM_CAP}[1:2]=        Set Variable    value_slice_as_str

    Length Should Be                  ${OBJECT_WITH_SETITEM_CAP.container}    4
    Dictionary Should Contain Item    ${OBJECT_WITH_SETITEM_CAP.container}    str_key    new_value
    Dictionary Should Contain Item    ${OBJECT_WITH_SETITEM_CAP.container}    0          value_str
    Dictionary Should Contain Item    ${OBJECT_WITH_SETITEM_CAP.container}    ${0}       value_int
    Dictionary Should Contain Item    ${OBJECT_WITH_SETITEM_CAP.container}    1:2        value_slice_as_str

Item assign to object without setitem capability fails
    [Documentation]    FAIL
    ...     Variable '\${OBJECT_WITHOUT_SETITEM_CAP}' is ObjectWithoutSetItemCap and does not support item assignment.
    ${OBJECT_WITHOUT_SETITEM_CAP}[newKey]=    Set Variable        newVal

Item assign to immutable object fails
    [Documentation]    FAIL
    ...     Variable '${tuple_variable}' is tuple and does not support item assignment.
    ${tuple_variable}=       Evaluate        (1,)
    ${tuple_variable}[0]=    Set Variable    0

Item assign expects iterable fails
    [Documentation]    FAIL STARTS:
    ...     Setting value to list variable '${list_variable}' at index [:1] failed: TypeError:
    ${list_variable}=       Create List    1    2    3
    ${list_variable}[:1]=   Evaluate       0

    Log To Console  ${list_variable}

Index not found error when item assign to list
    [Documentation]    FAIL STARTS:
    ...    Setting value to list variable '${list_variable}[0]' at index [2] failed: IndexError:
    ${list_variable}=        Create List    ${{ [1, 2] }}
    ${list_variable}[0][2]=  Set Variable   3

Item assign to undeclared scalar fails
    [Documentation]    FAIL    Variable '${undeclared_scalar}' not found.
    ${undeclared_scalar}[0]=  Set Variable   0

Item assign to undeclared dict fails
    [Documentation]    FAIL    Variable '${undeclared_dict}' not found.
    &{undeclared_dict}[0]=  Set Variable   0

Item assign to undeclared list fails
    [Documentation]    FAIL    Variable '${undeclared_list}' not found.
    @{undeclared_list}[0]=  Set Variable   0

Empty item assign to list fails
    [Documentation]    FAIL
    ...    Setting value to list variable '${list_variable}' at index [] failed: \
    ...    TypeError: list indices must be integers or slices, not str
    ${list_variable}=       Create List    ${{ [1, 2] }}
    ${list_variable}[]=     Set Variable   3

Empty item assign to dictionary
    ${dict_variable}=       Create Dictionary
    ${dict_variable}[]=     Set Variable       empty

    Dictionary Should Contain Item     ${dict_variable}      ${{ '' }}      empty

Multiple item assigns to scalars only
    ${list_variable}=                               Create List     ${1}    ${2}
    ${list_variable}[1]   ${list_variable}[${0}]=   Set Variable    @{list_variable}

    Should Be Equal       ${list_variable}          ${{ [2, 1] }}

Multiple item assigns to scalars and list
    ${list_variable}=    Create List        ${1}    ${2}
    ${dict_variable}=    Create Dictionary

    ${dict_variable}[abc]   ${dict_variable}[def]   @{list_variable}[1]=   Set Variable    ${{ ("first", "second", "list_element") }}

    Should Be Equal    ${list_variable}    ${{ [1, ["list_element"]] }}
    Should Be Equal    ${dict_variable}    ${{ {"abc": "first", "def": "second" } }}

Multiple item assigns to scalars and list slice
    ${list_variable}=    Create List        ${1}    ${2}
    ${dict_variable}=    Create Dictionary

    ${dict_variable}[abc]   ${dict_variable}[def]   @{list_variable}[1:]=   Set Variable    ${{ ("first", "second", "list_element") }}

    Should Be Equal    ${list_variable}    ${{ [1, "list_element"] }}
    Should Be Equal    ${dict_variable}    ${{ {"abc": "first", "def": "second" } }}

Item assign without assign mark
    ${dict_variable}        Create Dictionary
    ${dict_variable}[key]   Set Variable            val
    Should Be Equal         ${dict_variable}[key]   val

Single item assign to list
    @{list_variable}=         Create List    x  y  z
    @{list_variable}[1]=      Create List    a  b  c
    @{temp_list}=             Create List    0  1  2
    @{list_variable}[1][-1]=  Set Variable   ${temp_list}

    Should Be Equal   ${list_variable}    ${{ ['x', ['a', 'b', ['0', '1', '2']], 'z'] }}

    # Assert that the assigned list has been copied by changing the value of temp_list
    ${temp_list}[0]=       Set Variable        -1
    @{expected_list}=      Create List         0   1   2
    @{inner_list}=         Set Variable        @{list_variable}[1][-1]
    Lists Should Be Equal  ${inner_list}       ${expected_list}

Single item assign to dict
    &{dict_variable}=            Create Dictionary    x=y   a=b
    &{dict_variable}[a]=         Evaluate             {0:1, 2:3}
    &{dict_variable}[a][z]=      Evaluate             {'key': 'value'}

    Should Be Equal       ${dict_variable}    ${{ {'x': 'y', 'a': {0: 1, 2: 3, 'z': {'key': 'value'}}} }}

    # Assert that the dictionary is a DotDict (extended assign)
    ${inner_dict}=        Set Variable        ${dict_variable.a.z}
    Should Not Be Empty   ${inner_dict}

Single item assign to list should fail if value is not list
    [Documentation]    FAIL
    ...    Setting value to list variable '@{list_variable}' at index [1] failed: \
    ...    Expected list-like value, got string.
    @{list_variable}=          Create List     x  y  z
    @{list_variable}[1]=       Set Variable    abc

Single item assign to dict should fail if value is not dict
    [Documentation]    FAIL
    ...    Setting value to DotDict variable '&{dict_variable}' at index [1] failed: \
    ...    Expected dictionary-like value, got string.
    &{dict_variable}=          Create Dictionary    x=y   a=b
    &{dict_variable}[1]=       Set Variable         abc

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

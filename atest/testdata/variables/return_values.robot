*** Settings ***
Documentation     NO RIDE because it would sanitize formatting too much.
Library           ExampleLibrary
Library           Collections

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

None To Scalar Variable
    ${var} =    Evaluate    None
    Should Be True    ${var} is None
    Should Not Be Equal    ${var}    None

Unrepresentable object to scalar variable
    ${var} =    Return Unrepresentable Objects    identifier=xxx    just_one=True
    Should Be Equal    ${var.identifier}    xxx

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

Multiple Scalars With Too Few Values
    [Documentation]    FAIL Cannot assign return values: Need more values than 2.
    ${a}    ${b}    ${c} =    Create List    a    b

Scalar Variables With More Values Than Variables
    [Documentation]    Extra string variables are added to last scalar variable as list
    ${a}    ${b}    ${c} =    Create List    a    b    c    ${4}
    Should Be Equal    ${a}    a
    Should Be Equal    ${b}    b
    Should Be True    ${c} == ['c', 4]

Multiple Scalars When No List Returned 1
    [Documentation]    FAIL Cannot assign return values: Expected list-like object, got string instead.
    ${a}    ${b} =    Set Variable    This is not list

Multiple Scalars When No List Returned 2
    [Documentation]    FAIL Cannot assign return values: Expected list-like object, got int instead.
    ${a}    ${b} =    Set Variable    ${42}

List Variable
    @{listvar} =    Create List    h    e    ll    o
    Should Be Equal    @{listvar}[0]    h
    Should Be Equal    @{listvar}[1]    e
    Should Be Equal    @{listvar}[2]    ll
    Should Be Equal    @{listvar}[3]    o
    @{list} =    Create List
    Should Be Empty    ${list}

List Variable From Custom Iterable
    @{listvar} =    Return Custom Iterable    Keijo    Mela
    Should Be Equal    @{listvar}[0]    Keijo
    Should Be Equal    @{listvar}[1]    Mela

List Variable From List Subclass
    @{listvar} =    Return List Subclass    Keijo    Mela
    Should Be Equal    @{listvar}[0]    Keijo
    Should Be Equal    @{listvar}[1]    Mela

List Variable From Dictionary
    @{list} =    Create Dictionary    name=value
    Should Be Equal    @{list}    name
    Should Be True    ${list} == ['name']
    @{list} =    Create Dictionary    a=1    b=2    c=3
    Should Be True    set(${list}) == set(['a', 'b', 'c'])

Unrepresentable objects to list variables
    @{unrepr} =    Return Unrepresentable Objects    identifier=list
    Length Should Be    ${unrepr}    2
    :FOR    ${obj}    IN    @{unrepr}
    \    Should Be Equal    ${obj.identifier}    list
    \    ${var} =    Set Variable    ${obj}
    \    Should Be Equal    ${var}    ${obj}

List When No List Returned
    [Documentation]    FAIL Cannot assign return values: Expected list-like object, got int instead.
    @{list} =    Set Variable    ${42}

Scalars And And List
    ${first}    @{rest} =    Evaluate    range(5)
    Should Be Equal    ${first}    ${0}
    Should Be True    @{rest} == [1, 2, 3, 4]
    ${a}    ${b}    @{c} =    Create List    1    2    c    d    e    f
    Should Be Equal   ${a} + ${b}    1 + 2
    Should Be True    @{c} == ['c', 'd', 'e', 'f']

None To Multiple Scalar Variables
    ${x}    ${y} =    Run Keyword If    False    Not Executed
    Should Be Equal    ${x}    ${None}
    Should Be Equal    ${y}    ${None}

None To List Variable
    @{list} =    Log    This returns None
    Should Be True    @{list} == []

None To Scalar Variables And List Variable
    ${a}    ${b}    ${c}    @{d} =    No Operation
    Should Be Equal    ${a}    ${None}
    Should Be Equal    ${b}    ${None}
    Should Be Equal    ${c}    ${None}
    Should Be True    @{d} == []

List Variable Can Be Only Last 1
    [Documentation]    FAIL Only the last variable to assign can be a list variable.
    @{list}    @{list2} =    Set Variable    1    2

List Variable Can Be Only Last 2
    [Documentation]    FAIL Only the last variable to assign can be a list variable.
    @{list}    ${scalar} =    Set Variable    1    2

Long String To Scalar Variable
    ${v300} =    Evaluate    '123456789 ' * 30
    Length Should Be    ${v300}    300

Long Values To List Variable
    ${v99} =    Evaluate    ('123456789 ' * 10).strip()
    @{long} =    Create List    ${v99}    ${v99}    ${v99}
    Should Be Equal    @{long}[0]    ${v99}
    Should Be Equal    @{long}[1]    ${v99}
    Should Be Equal    @{long}[2]    ${v99}

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
    Should Be Equal    @{list}[0] @{list}[1] @{list}[2]    a b c

No Assign Mark
    ${var}    Set Variable    hello
    Should Be Equal    ${var}    hello
    ${v1}    ${v2}    Set Variable    hi    you
    Should Be Equal    ${v1}    hi
    Should Be Equal    ${v2}    you
    @{list}    Set Variable    a    b    c
    Should Be Equal    @{list}[0] @{list}[1] @{list}[2]    a b c

Optional Assign Mark With Multiple Variables
    ${a}    ${b} =    Set Variable    a    b
    Should Be Equal    ${a}-${b}    a-b
    ${a}    ${b}    @{c}=    Set Variable    a    b    c
    Should Be Equal    ${a}-${b}    a-b
    Should Be Equal    @{c}    c

Assign Mark Can Be Used Only With The Last Variable
    [Documentation]    FAIL Assign mark '=' can be used only with the last variable.
    ${v1} =    ${v2} =    Set Variable    a    b

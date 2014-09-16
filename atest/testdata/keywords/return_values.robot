*** Settings ***
Documentation   NO RIDE because it would sanitize formatting too much.
Library         ExampleLibrary

*** Test Cases ***
Simple Scalar Variable
    ${setvar} =  Set Variable  this value is set
    Should Be Equal  ${setvar}  this value is set

Empty Scalar Variable
    ${setvar} =  Set Variable  ${EMPTY}
    Should Be Equal  ${setvar}  ${EMPTY}

List To Scalar Variable
    ${setvar} =  Create List  a  ${2}
    Should Be Equal  ${setvar[0]}  a
    Should Be Equal  ${setvar[1]}  ${2}

Multible Scalar Variables
    ${var1}  ${var2} =  Create List  one  two
    Should Be Equal  ${var1}  one
    Should Be Equal  ${var2}  two

= Mark Without Space
    ${var}=  Set Variable  hello
    Should Be Equal  ${var}  hello
    ${v1}  ${v2}=  Set Variable  hi  you
    Should Be Equal  ${v1}  hi
    Should Be Equal  ${v2}  you
    @{list}=  Set Variable  a  b  c
    Should Be Equal  @{list}[0] @{list}[1] @{list}[2]  a b c

No = Mark
    ${var}  Set Variable  hello
    Should Be Equal  ${var}  hello
    ${v1}  ${v2}  Set Variable  hi  you
    Should Be Equal  ${v1}  hi
    Should Be Equal  ${v2}  you
    @{list}  Set Variable  a  b  c
    Should Be Equal  @{list}[0] @{list}[1] @{list}[2]  a b c

Optional = Mark With Multiple Variables
    ${v1}  ${v2}  @{list}=  Set Variable  a  b  c
    Should Be Equal  ${v1}  a
    Should Be Equal  ${v2}  b
    Should Be Equal  @{list}  c

= Can Be Used Only With The Last Variable
    [Documentation]  FAIL Assign mark '=' can be used only with the last variable.
    ${v1} =  ${v2} =  Set Variable  a  b

Python Object To Scalar Variable
    ${var} =  Return Object  This is my name
    Should Be Equal  ${var.name}  This is my name

None To Scalar Variable
    ${var} =  Evaluate  None
    Fail Unless  ${var} is None
    Fail If Equal  ${var}  None

List Variable
    @{listvar} =  Create List  h  e  ll  o
    Should Be Equal  @{listvar}[0]  h
    Should Be Equal  @{listvar}[1]  e
    Should Be Equal  @{listvar}[2]  ll
    Should Be Equal  @{listvar}[3]  o

List Variable From Custom Iterable
    @{listvar} =  Return Custom Iterable  Keijo  Mela
    Should Be Equal  @{listvar}[0]  Keijo
    Should Be Equal  @{listvar}[1]  Mela

List Variable From List Subclass
    @{listvar} =  Return List Subclass  Keijo  Mela
    Should Be Equal  @{listvar}[0]  Keijo
    Should Be Equal  @{listvar}[1]  Mela

Long String To Scalar Variable
    ${var_300} =  Set Variable  123456789 123456789 123456789 123456789 123456789 123456789 123456789 123456789 123456789 1234567890123456789 123456789 123456789 123456789 123456789 123456789 123456789 123456789 123456789 1234567890123456789 123456789 123456789 123456789 123456789 123456789 123456789 123456789 123456789 1234567890
    Should Be Equal  123456789 123456789 123456789 123456789 123456789 123456789 123456789 123456789 123456789 1234567890123456789 123456789 123456789 123456789 123456789 123456789 123456789 123456789 123456789 1234567890123456789 123456789 123456789 123456789 123456789 123456789 123456789 123456789 123456789 1234567890  ${var_300}

Long Values To List Variable
    ${100_marks} =  Set Variable  123456789 123456789 123456789 123456789 123456789 123456789 123456789 123456789 123456789 1234567890
    @{listvar} =  Create List  ${100_marks}  ${100_marks}  ${100_marks}
    Should Be Equal  ${100_marks}  @{listvar}[0]
    Should Be Equal  ${100_marks}  @{listvar}[1]
    Should Be Equal  ${100_marks}  @{listvar}[2]

Scalar Variables With More Values Than Variables
    [Documentation]  Extra string variables are added to last scalar variable as list
    ${a}  ${b}  ${c} =  Create List  a  b  c  ${4}
    Should Be Equal  ${a}  a
    Should Be Equal  ${b}  b
    Should Be True  ${c} == ['c', 4]

Multiple Scalars With Too Few Values
    [Documentation]  FAIL Cannot assign return values: Need more values than 2.
    ${a}  ${b}  ${c} =  Create List  a  b

Multiple Scalars When No List Returned
    [Documentation]  FAIL Cannot assign return values: Expected list-like object, got string instead.
    ${a}  ${b} =  Set Variable  This is not list

List When No List Returned
    [Documentation]  FAIL Cannot assign return values: Expected list-like object, got int instead.
    @{list} =  Set Variable  ${42}

List To Scalar And List Variables
    ${a}  ${b}  @{c} =  Create List  1  2  c  d  e  f
    Should Be True  ${a} + ${b} == 3
    Should Be True  @{c} == ['c', 'd', 'e', 'f']
    Should Be Equal  @{c}[1]@{c}[2]@{c}[3] @{c}[3]oo(@{c}[0]): print @{c}[0]  def foo(c): print c

One None To Multiple Variables
    ${x}  ${y} =  Run Keyword If  False  Not Executed
    Should Be Equal  ${x}  ${None}
    Should Be Equal  ${y}  ${None}

One None To List Variable
    @{list} =  Log  This returns None
    Should Be True  @{list} == []

One None To Scalar Variables And List Variable
    ${a}  ${b}  ${c}  @{d} =  No Operation
    Should Be Equal  ${a}  ${None}
    Should Be Equal  ${b}  ${None}
    Should Be Equal  ${c}  ${None}
    Should Be True  @{d} == []

List Variable Can Be Only Last 1
    [Documentation]  FAIL Only the last variable to assign can be a list variable.
    @{list}  @{list2} =  Set Variable  1  2

List Variable Can Be Only Last 2
    [Documentation]  FAIL Only the last variable to assign can be a list variable.
    @{list}  ${scalar} =  Set Variable  1  2

No Keyword
    [Documentation]  FAIL Keyword name cannot be empty.
    ${nokeyword}

Failing Keyword
    [Documentation]  FAIL Failing instead of returning
    ${ret} =  Fail  Failing instead of returning

Failing Keyword And Teardown
    [Documentation]  FAIL Failing, again, instead of returning\n  \n  Also teardown failed:\n  Teardown fails but it is executed normally
    ${ret} =  Fail  Failing, again, instead of returning
    [Teardown]  Fail  Teardown fails but it is executed normally

Return Unrepresentable Objects
    ${o1}  ${o2}=  Return Unrepresentable Objects

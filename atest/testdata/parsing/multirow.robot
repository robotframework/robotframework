*** Settings ***
...  # Invalid usage
Documentation   NO RIDE!!\
...  This  doc  is  one  long  string
...  !
\  ...  !
\  \  ...  !
...  !
# Some comments here to complicate parsing even more ...
Default Tags  ...  t1  t2  t3  t4
...           t4  t5  \   t6
...
...           # more comments
\  ...           \   t7  t8
...           t9
Library
...  OperatingSystem


*** Variables ***
...  # Invalid usage
@{scalarlist}  1  2  3  4
...  5  6  7
...  8
...
...  9  10
# Comments, comments, comments, ...
${string}
...  some text
...
@{list}  ...  hello
...  world
...
\  ...  ...


*** Test Cases ***
\   ...  # Invalid usage
    [Documentation]  FAIL Test case name cannot be empty.
    No Operation

Invalid Usage In Test And User Keyword
    ...
    [Documentation]  FAIL This is executed after all!
    Invalid Usage In UK

Multirow Variables
    Should Be True  ${scalarlist} == [str(i) for i in range(1,11)]
    Should Be Equal  ${string}  some text
    Should Be Equal  @{list}[0]  ...
    Should Be Equal  @{list}[1]  hello
    Should Be Equal  @{list}[2]  world
    Should Be Equal  @{list}[3]  ...

Multirow Import
    Directory Should Exist  .

Multirow Args For Library Keyword
    Log Many  one  two
    ...  three
    ...
    \  \  \  \  ...
    \  \  ...  four  five

Multirow Args For User Keyword
    UK Log Many
    ...  ${1}
    ...
    ...  ${2}  ${3}
    \  ...  ${4}
    ...  ${5}

Multirow Return Values
    ${x} =  Create List  0  1
    ...  2  3  4  5
    ...  6  7  8
    ...
    \  ...  9
    Should Be True  ${x} == [str(i) for i in range(10)]
    ${a}  ${b}  ${c}  ${d} =  Create List  1
    ...     2     3
    \   \  ...  4
    Should Be Equal  ${a}  1
    Should Be Equal  ${b}  2
    Should Be Equal  ${c}  3
    Should Be Equal  ${d}  4

Multirow In User Keyword
    Multirow In User Keyword

Multirow Test Settings
    [Documentation]  This  test  doc\
    ...  is\
    \   ...  one\
    ...
    ...  long  string
    [Tags]
    ...  my1  my2  my3
    ...  my4
    ...
    \  ...  \  \  \  \  my5
    No Operation

Multirow User Keyword Settings
    ${x} =  Multirow User Keyword Settings  1  2
    Should Be True  ${x} == [str(i) for i in range(1,10)]
    ${x} =  Multirow User Keyword Settings
    ...  1  2  3  4  5  r1  r2  r3
    Should Be True  ${x[:5]} == [str(i) for i in range(1,6)]
    Should Be True  ${x[5:8]} == ['r1','r2','r3']
    Should Be True  ${x[9:]} == [str(i) for i in range(7,10)]

Multirow With For Loop Declaration
    ${result} =  Set Variable  ${EMPTY}
    :FOR  ${item}  IN  a  b
    ...                c
    \  ${result} =  Set Variable  ${result}${item}
    Should Be Equal  ${result}  abc
    :FOR
    ...  ${item}
    ...  IN
    ...  c
    ...  b
    \  ${result} =  Set Variable  ${result.replace('${item}', '')}
    Should Be Equal  ${result}  a
    :FOR
    ...  ${item}
    ...  IN RANGE
    ...  1
    ...  2
    \  ${result} =  Set Variable  ${result}${item}
    Should Be Equal  ${result}  a1
    :FOR  ${i1}  ${i2}  IN
    ...   b      2
    ...   c      3
    \  ${result} =  Set Variable  ${result}${i1}${i2}
    Should Be Equal  ${result}  a1b2c3
    :FOR  ${item}  IN
    \  ...  a  b  c
    \  ${result} =  Set Variable  ${result.replace('${item}', '')}
    Should Be Equal  ${result}  123
    :FOR  ${item}  IN RANGE  1
    \  \  \  ...  4
    \  ${result} =  Set Variable  ${result.replace('${item}', '')}
    Should Be Equal  ${result}  ${EMPTY}

Multirow With For Loop Keywords
    ${result} =  Set Variable  ${EMPTY}
    :FOR  ${item}  IN  a  b  c
    \  ${item} =  Set Variable
    \  ...  ${item.upper()}
    \  ${result} =  Set Variable
    ...  ${result}${item}
    \    ${x} =
    ...  Catenate
    ...     1  2  3
    \  ...  a
    \  ...     b
    \  \  ...        ${item.lower()}
    Should Be Equal  ${result}  ABC
    Should Be Equal  ${x}  1 2 3 a b c




*** Keywords ***
\    # Invalid usage

Invalid Usage In UK
    ...
    Fail  This is executed after all!

UK Log Many
    [Arguments]  @{msgs}
    Log Many  @{msgs}

Multirow In User Keyword
    Log Many
    ...  1
    \  \  ...  2
    UK Log Many
    ...  xxx
    ${y} =  Create List  1  2
    ...  3  4  5
    Should Be True  ${y} == [str(i) for i in range(1,6)]
    @{z} =  Create List
    ...  aaa  bbb
    Should Be True  ${z} == ['aaa', 'bbb']

Multirow User Keyword Settings
    [Arguments]  ${a1}  ${a2}  ${a3}=3
    ...  ${a4}=4
    \  ...
    \  ...  ${a5}=5  @{rest}
    ...
    Should Be Equal  ${a1}  1
    Should Be Equal  ${a2}  2
    Should Be Equal  ${a3}  3
    Should Be Equal  ${a4}  4
    Should Be Equal  ${a5}  5
    [Return]  ${a1}  ${a2}
    ...  ${a3}  ${a4}  ${a5}
    ...
    \  ...  @{rest}
    ...  6
    ...  7
    ...  8
    \  \   ...  9

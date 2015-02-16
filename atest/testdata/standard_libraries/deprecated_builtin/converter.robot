*** Test Case ***
Integer
    ${plus1}    Integer    1
    Should Be Equal    ${plus1}    ${1}
    Should Be True    ${plus1} + ${plus1} == 2
    ${minus42}    Integer    -42
    Should Be Equal    ${minus42}    ${-42}
    ${googol}    Integer    10000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
    Should Be True    ${googol} == 10**100L

Float
    ${minus10}    Float    -10.000
    Should Be Equal    ${minus10}    ${-10}
    ${e}    Float    2.7182818284590451
    Should Be True    round(__import__('math').log(${e}), 8) == 1.0

String
    ${str42}    String    ${42}
    Should Be Equal    ${str42}    42

Boolean
    ${True}    Boolean    True
    ${False}    Boolean    false
    Should Be True    ${True} == True
    Should Be True    ${False} == False
    ${True}    Boolean    ${1}
    ${False}    Boolean    ${0}
    Should Be True    ${True} == True
    Should Be True    ${False} == False

List
    ${list}    List    hello    world
    Should Be True    ${list} == ['hello','world']
    @{list}    List    hello    world
    Should Be Equal    @{list}[0]    hello
    Should Be Equal    @{list}[1]    world
    ${one_item}    List    one item
    Should Be True    ${one_item} == ['one item']
    ${empty}    List
    Should Be True    ${empty} == [ ]
    ${mixed}    List    one    ${1}
    Should Be True    ${mixed} == ['one', 1]

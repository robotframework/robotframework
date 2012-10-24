*** Test Case ***
Integer
    ${plus1}    Integer    1
    Fail Unless Ints Equal    ${plus1}    1
    Fail Unless    ${plus1} + ${plus1} == 2
    ${minus42}    Integer    -42
    Fail Unless Ints Equal    ${minus42}    -42
    ${googol}    Integer    10000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
    Fail Unless    ${googol} == 10**100L

Float
    ${minus10}    Float    -10.000
    Fail Unless Floats Equal    ${minus10}    -10
    ${e}    Float    2.7182818284590451
    Fail Unless    round(__import__('math').log(${e}), 8) == 1.0

String
    ${int42}    Integer    42
    Fail If Equal    ${int42}    42
    ${str42}    String    ${int42}
    Fail Unless Equal    ${str42}    42

Boolean
    ${True}    Boolean    True
    ${False}    Boolean    false
    Fail Unless    ${True} == True
    Fail Unless    ${False} == False
    ${one}    Integer    1
    ${zero}    Integer    0
    ${True}    Boolean    ${one}
    ${False}    Boolean    ${zero}
    Fail Unless    ${True} == True
    Fail Unless    ${False} == False

List
    ${list}    List    hello    world
    Fail Unless    ${list} == ['hello','world']
    @{list}    List    hello    world
    Equals    @{list}[0]    hello
    Equals    @{list}[1]    world
    ${one_item}    List    one item
    Fail Unless    ${one_item} == ['one item']
    ${empty}    List
    Fail Unless    ${empty} == [ ]
    ${int_one}    Integer    1
    ${mixed}    List    one    ${int_one}
    Fail Unless    ${mixed} == ['one', 1]


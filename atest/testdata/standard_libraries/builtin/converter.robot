*** Settings ***
Variables       numbers_to_convert.py

*** Test Cases ***
Convert To Integer
    [Documentation]    FAIL STARTS: 'MyObject' cannot be converted to an integer: ZeroDivisionError:
    [Template]    Test Convert To Integer
    1                    1
    -42                  -42
    10000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
    ...                  10**100
    ${OBJECT}            42
    ${OBJECT_FAILING}    This fails!

Convert To Integer With Base
    [Documentation]    FAIL STARTS: 'A' cannot be converted to an integer: ValueError:
    [Template]    Test Convert To Integer
    10           10        10
    A            10        16
    -10          -8        ${8}
    +10          8         ${8}
    10           2         2
    -FF 00       -65280    16
    1010 1010    170       2
    A            fails

Convert To Integer With Invalid Base
    [Documentation]    FAIL STARTS: '1' cannot be converted to an integer: 'invalid' cannot be converted to an integer: ValueError:
    Convert To Integer    1    invalid

Convert To Integer With Embedded Base
    [Documentation]    FAIL STARTS: '0xXXX' cannot be converted to an integer: ValueError:
    [Template]    Test Convert To Integer
    0xf00           3840
    -0XF00          -3840
    0b10            2
    -0B10           -2
    +0B10           2
    0B10            2832    base=16    # Explicit base wins
    0o101           65
    0O102           66
    - 0x FF 00      -65280
    + 0x FF 00      65280
    0b 1010 1010    170
    0xXXX           fails

Convert To Binary
    [Template]    Test Convert To Binary
    0             0
    1             ${1}
    -10           ${-2}
    0b10          2        prefix=0b
    -0b10         -2       prefix=0b
    0b10          +2       prefix=0b
    00001000      10       base=8     length=8
    11111111      0xFF
    -11111111     -0xFF
    11111111      +0xFF
    -100000000    -100     base=16    length=2
    B0101         101      base=2     prefix=B    length=4

Convert To Octal
    [Template]    Test Convert To Octal
    0            0
    1            ${1}
    -2           ${-2}
    0o10         8            prefix=0o
    -0o10        -8           prefix=0o
    0o10         +8           prefix=0o
    00001000     200          base=16    length=8
    52746757     +0xABCDEF    length=5
    -52746757    -0xABCDEF    length=5
    xXx007       111          base=2     prefix=xXx    length=3

Convert To Hex
    [Template]    Test Convert To Hex
    0          0
    1          ${1}
    -2         ${-2}
    0xA        10       prefix=0x    length=0
    -0xA       -10      prefix=0x    length=0
    0xA        +0o12    prefix=0x    length=0
    0000abcd   ABCD     base=16      length=8     lowercase=yes
    -0A0a      -10      base=10      prefix=0A    lowercase=please    length=2

Convert To Number
    [Documentation]    FAIL REGEXP: ^'MyObject' cannot be converted to a floating point number: (Attribute|Type)Error: .*$
    [Template]    Test Convert To Number
    -10.000              -10
    ${OBJECT}            42.0
    ${OBJECT_FAILING}    This fails!

Convert To Number With Precision
    [Documentation]    FAIL STARTS: 'invalid' cannot be converted to an integer: ValueError:
    [Template]    Test Convert To Number With Precision
    1.01      0          1
    1.02      ${0}       1
    1.03      ${NONE}    1.03
    1.14      1          1.1
    9.1      -1          10
    1         invalid    This fails!

Numeric conversions with long types
    [Template]    Numeric conversions with long types
    # 0x8000000000000000 == sys.maxint+1 on 64bit machines
    Convert To Integer    0                     0
    Convert To Integer    42                    42
    Convert To Integer    0x8000000000000000    9223372036854775808
    Convert To Hex        0                     0
    Convert To Hex        42                    2A
    Convert To Hex        0x8000000000000000    8000000000000000
    Convert To Octal      0                     0
    Convert To Octal      42                    52
    Convert To Octal      0x8000000000000000    1000000000000000000000
    Convert To Binary     0                     0
    Convert To Binary     42                    101010
    Convert To Binary     0x8000000000000000    1000000000000000000000000000000000000000000000000000000000000000

Convert To String
    ${int42} =    Convert To Integer    42
    Should Not Be Equal    ${int42}    42
    ${str42} =    Convert To String    ${int42}
    Should Be Equal    ${str42}    42

Convert To Boolean
    ${True} =    Convert To Boolean    True
    ${False} =    Convert To Boolean    false
    Should Be True    ${True} == True
    Should Be True    ${False} == False
    ${one} =    Convert To Integer    1
    ${zero} =    Convert To Integer    0
    ${True} =    Convert To Boolean    ${one}
    ${False} =    Convert To Boolean    ${zero}
    Should Be True    ${True} == True
    Should Be True    ${False} == False

Create List
    ${list} =    Create List    hello    world
    Should Be True    ${list} == ['hello','world']
    @{list} =    Create List    hello    world
    Should Be Equal    ${list}[0]    hello
    Should Be Equal    ${list}[1]    world
    ${one_item} =    Create List    one item
    Should Be True    ${one_item} == ['one item']
    ${empty} =    Create List
    Should Be True    ${empty} == [ ]
    ${int_one} =    Convert To Number    1
    ${mixed} =    Create List    one    ${int_one}
    Should Be True    ${mixed} == ['one', 1]

*** Keywords ***
Test Convert To Integer
    [Arguments]    ${item}    ${exp}=1    ${base}=
    ${act} =    Convert To Integer    ${item}    ${base}
    ${exp} =    Evaluate    ${exp}
    Should Be Equal    ${act}    ${exp}

Test Convert To Binary
    [Arguments]    ${exp}    ${item}    ${base}=    ${prefix}=    ${length}=
    ${act} =    Convert To Binary    ${item}    base=${base}
    ...    prefix=${prefix}    length=${length}
    Should Be Equal    ${act}    ${exp}

Test Convert To Octal
    [Arguments]    ${exp}    ${item}    ${base}=    ${prefix}=    ${length}=
    ${act} =    Convert To Octal    ${item}    base=${base}
    ...    prefix=${prefix}    length=${length}
    Should Be Equal    ${act}    ${exp}

Test Convert To Hex
    [Arguments]    ${exp}    ${item}    ${base}=    ${prefix}=    ${length}=    ${lowercase}=
    ${act} =    Convert To Hex    ${item}    base=${base}
    ...    prefix=${prefix}    length=${length}    lowercase=${lowercase}
    Should Be Equal    ${act}    ${exp}

Test Convert To Number
    [Arguments]    ${item}    ${exp}=1.0
    ${act} =    Convert To Number    ${item}
    Should Be True    round(${act}, 6) == ${exp}

Test Convert To Number With Precision
    [Arguments]    ${item}    ${precision}    ${exp}
    ${act} =    Convert To Number    ${item}    ${precision}
    Should Be True    round(${act}, 6) == ${exp}

Numeric conversions with long types
    [Arguments]    ${keyword}    ${input}    ${expected}
    ${input} =    Evaluate    (long if sys.version_info[0] == 2 else int)(${input})    modules=sys
    ${result} =    Run Keyword    ${keyword}    ${input}
    Should Be Equal As Strings    ${result}    ${expected}

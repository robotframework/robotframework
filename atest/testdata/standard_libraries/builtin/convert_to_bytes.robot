*** Settings ***
Test Template    Correct bytes should be created
Library          String

*** Variables ***
@{CHAR LIST}     h    y    v    ä    \x00
@{INT LIST}      0    ${1}    0b10    0o3    0xff
@{HEX LIST}      0    1    007    ff
@{BIN LIST}      0    1    111    11111111
@{BIG LIST}      100000000
@{SMALL LIST}    -1

*** Test Cases ***
Default input type is text
    [Template]    NONE
    ${bytes} =    Convert To Bytes    Tämä on testi
    Bytes should be equal to    ${bytes}    84, 228, 109, 228, 32, 111, 110, 32, 116, 101, 115, 116, 105
    ${bytes} =    Convert To Bytes    0 1 2    input_type=int
    Bytes should be equal to    ${bytes}    0, 1, 2

Invalid input type fails
    [Template]    Creating bytes should fail
    whatever    invalid    Invalid input type 'invalid'.

ASCII string
    H           text    72
    hello       text    104, 101, 108, 108, 111
    \x00\x01    text    0, 1
    0 1 2       text    48, 32, 49, 32, 50

Non-ASCII string
    åäö         text    229, 228, 246
    \xe4\xff    text    228, 255

Non-ASCII above 255 fails
    [Template]    Creating bytes should fail
    \u0100      text    Character '\u0100' cannot be represented as a byte.
    \u2603      text    Character '\u2603' cannot be represented as a byte.

Characters as a list
    ${CHAR LIST}    text    104, 121, 118, 228, 0

Byte string
    [Template]    NONE
    ${b1} =    Convert To Bytes    \x00-a-ä-\xff
    ${b2} =    Convert To Bytes    ${b1}
    Should Be Equal    ${b1}    ${b2}

Bytearray
    [Template]    NONE
    ${bytearray} =    Evaluate    bytearray([0, 1, 2, 255])
    ${bytes} =    Convert To Bytes    ${bytearray}
    ${expected} =    Convert To Bytes    \x00\x01\x02\xff
    Should Be Equal    ${bytes}    ${expected}

Integers
    4                      int    4
    0 255                  int    0, 255
    104 101 108 108 111    int    104, 101, 108, 108, 111
    0 1 2 3 4              int    0, 1, 2, 3, 4

Any whitespace as integer separator
    0\t1 255               int    0, 1, 255
    0\n1${SPACE*5}2\r33    int    0, 1, 2, 33

Integers with prefixes
    0b111 0B0010           int    7, 2
    0o111 0O0010           int    73, 8
    0xF 0X0f               int    15, 15
    0b10 0o10 10 0x10      int    2, 8, 10, 16
    0b11111111 0o377 0xff  int    255, 255, 255

Integers as list
    ${INT LIST}    int    0, 1, 2, 3, 255

Integer as integer
    ${0}     int    0
    ${42}    int    42

Integers without separators does not work
    [Template]    Creating bytes should fail
    001007    int    Integer '001007' cannot be represented as a byte.

Too big or small integers
    [Template]    Creating bytes should fail
    256 1            int    Integer '256' cannot be represented as a byte.
    0 0xfff          int    Integer '0xfff' cannot be represented as a byte.
    -1               int    Integer '-1' cannot be represented as a byte.
    ${BIG LIST}      int    Integer '100000000' cannot be represented as a byte.
    ${SMALL LIST}    int    Integer '-1' cannot be represented as a byte.

Invalid integers
    [Template]    Creating bytes should fail
    hello 1      int    'hello' cannot be converted to an integer: ValueError: *
    0 0xa 0ba    int    '0ba' cannot be converted to an integer: ValueError: *

Hex without whitespace
    0a                 hex    10
    aBbA               hex    171, 186
    000102ff           hex    0, 1, 2, 255
    68656c6C6f         hex    104, 101, 108, 108, 111

Hex with whitespace
    68 65 6c 6C 6f     hex    104, 101, 108, 108, 111
    6865 6c6C 6f       hex    104, 101, 108, 108, 111
    6 8 6 5 6 c 6 C    hex    104, 101, 108, 108
    01\t02\n\r03       hex    1, 2, 3
    f${SPACE*10}f      hex    255

Hex requires even input
    [Template]    Creating bytes should fail
    abc     hex    Expected input to be multiple of 2.
    ab c    hex    Expected input to be multiple of 2.

Hex as list
    ${HEX LIST}    hex    0, 1, 7, 255

Too big or small hex
    [Template]    Creating bytes should fail
    ${BIG LIST}      hex    Hex value '100000000' cannot be represented as a byte.
    ${SMALL LIST}    hex    Hex value '-1' cannot be represented as a byte.

Invalid hex
    [Template]    Creating bytes should fail
    ff hello!    hex     'he' cannot be converted to an integer: ValueError: *

Binary without spaces
    00000000                     bin   0
    0000000000000001             bin   0, 1
    000000110000111111111111     bin   3, 15, 255

Binary with whitespace
    0000 0000                    bin   0
    00 00 00 00 00 00 00 01      bin   0, 1
    0 0 0 0 0 0 1 1 0000 1111    bin   3, 15

Binary requires input to be multiple of 8
    [Template]    Creating bytes should fail
    00000000111111110    bin    Expected input to be multiple of 8.
    0000 0000 1111       bin    Expected input to be multiple of 8.

Binary as list
    ${BIN LIST}    bin    0, 1, 7, 255

Invalid binary
    [Template]    Creating bytes should fail
    hello!!!            bin    'hello!!!' cannot be converted to an integer: ValueError: *
    0000000100000002    bin    '00000002' cannot be converted to an integer: ValueError: *

Too big or small binary
    [Template]    Creating bytes should fail
    ${BIG LIST}         bin    Binary value '100000000' cannot be represented as a byte.
    ${SMALL LIST}       bin    Binary value '-1' cannot be represented as a byte.

*** Keywords ***
Correct bytes should be created
    [Arguments]    ${input}    ${type}    ${expected}
    ${bytes} =    Convert To Bytes    ${input}    ${type}
    Bytes should be equal to    ${bytes}    ${expected}

Bytes should be equal to
    [Arguments]    ${bytes}    ${expected}
    ${expected} =    Evaluate    bytes(bytearray(int(i) for i in [${expected}]))
    Should Be Equal    ${bytes}   ${expected}
    Should Be Byte String    ${bytes}

Creating bytes should fail
    [Arguments]    ${input}    ${type}    ${error}
    Run Keyword And Expect Error    Creating bytes failed: ${error}
    ...    Convert To Bytes    ${input}    ${type}

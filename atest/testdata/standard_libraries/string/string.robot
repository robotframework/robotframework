*** Settings ***
Library           String

*** Variables ***
${NSN}                nokia_siemens_networks
${TEXT IN COLUMNS}    robot\tframework\nis\tgood\tfor\ttesting
${FIRST LINE}         robot\tframework
${SECOND LINE}        is\tgood\tfor\ttesting

*** Test Cases ***
Fetch From Left
    ${result} =    Fetch From Left    ${NSN}    _siemens
    Should be Equal    ${result}    nokia

Fetch From Left with bytes
    ${result} =    Fetch From Left    ${{b"Robot Framework Foundation"}}    ${{b"Frame"}}
    Should be Equal    ${result}    Robot${SPACE}    type=bytes
    ${result} =    Fetch From Left    ${{b"Robot Framework Foundation"}}    ${SPACE}F
    Should be Equal    ${result}    Robot    type=bytes

Fetch From Right
    ${result} =    Fetch From Right    ${NSN}    _siemens_
    Should Be Equal    ${result}    networks

Fetch From Right with bytes
    ${result} =    Fetch From Right    ${{b"Robot Framework Foundation"}}    ${{b"ork "}}
    Should be Equal    ${result}    Foundation    type=bytes
    ${result} =    Fetch From Right    ${{b"Robot Framework Foundation"}}    ${SPACE}
    Should be Equal    ${result}    Foundation    type=bytes

Get Line
    ${result} =    Get Line    ${TEXT IN COLUMNS}    0
    Should be equal    ${result}    ${FIRST LINE}
    ${result} =    Get Line    ${TEXT IN COLUMNS}    1
    Should be equal    ${result}    ${SECOND LINE}

Get Line with bytes
    ${result} =    Get Line    ${{b"L1\nL2\nL3\nL4\nL5"}}    -1
    Should Be Equal    ${result}    L5    type=bytes

Get Line Count
    ${result} =    Get Line Count    ${EMPTY}
    Should Be Equal    ${result}    0    type=int
    ${result} =    Get Line Count    ${SPACE}
    Should Be Equal    ${result}    1    type=int
    ${result} =    Get Line Count    ${TEXT IN COLUMNS}
    Should Be Equal    ${result}    2    type=int

Get Line Count with bytes
    ${result} =    Get Line Count    ${{b"1\n2\n3\n4\n5"}}
    Should Be Equal    ${result}    5    type=int

Split To Lines
    @{result} =    Split To Lines    ${TEXT IN COLUMNS}
    Length Should Be    ${result}    2
    Should be equal    ${result}[0]    ${FIRST LINE}
    Should be equal    ${result}[1]    ${SECOND LINE}
    @{result} =    Split To Lines    Just one line!
    Length Should Be    ${result}    1
    Should be equal    ${result}[0]    Just one line!
    @{result} =    Split To Lines    ${EMPTY}
    Length Should Be    ${result}    0

Split To Lines With Start Only
    @{result} =    Split To Lines    ${TEXT IN COLUMNS}    1
    Should be equal    ${result}[0]    ${SECOND LINE}

Split To Lines With Start And End
    @{result} =    Split To Lines    ${TEXT IN COLUMNS}    0    1
    Length Should Be    ${result}    1
    Should be equal    ${result}[0]    ${FIRST LINE}

Split To Lines With End Only
    @{result} =    Split To Lines    ${TEXT IN COLUMNS}    end=1
    Length Should Be    ${result}    1
    Should be equal    ${result}[0]    ${FIRST LINE}

Split To Lines with empty string as start index is deprecated
    @{result} =    Split To Lines    ${TEXT IN COLUMNS}    ${EMPTY}    1
    Length Should Be    ${result}    1
    Should be equal    ${result}[0]    ${FIRST LINE}

Split To Lines With Negative Values
    @{result} =    Split To Lines    ${TEXT IN COLUMNS}    -1
    Length Should Be    ${result}    1
    Should be equal    ${result}[0]    ${SECOND LINE}

Split To Lines With Invalid Start
    [Documentation]    FAIL ValueError: Argument 'start' got value 'invalid' that cannot be converted to integer, '' or None.
    Split To Lines    ${TEXT IN COLUMNS}    invalid

Split To Lines With Invalid End
    [Documentation]    FAIL ValueError: Argument 'end' got value 'invalid' that cannot be converted to integer, '' or None.
    Split To Lines    ${TEXT IN COLUMNS}    0    invalid

Split To Lines with bytes
    @{result} =    Split To Lines    ${{b"1\n2\n3\n4\n5"}}
    Length Should Be    ${result}    5
    Should be equal    ${result}    ["1", "2", "3", "4", "5"]    type=list[bytes]

Get Substring
    ${result} =    Get Substring    Robot    0    2
    Should be equal    ${result}    Ro

Get Substring With Negative Values
    ${result} =    Get Substring    Hello Robot    -3    -1
    Should be equal    ${result}    bo

Get Substring With Start Only
    ${result} =    Get Substring    Hello Robot    6
    Should be equal    ${result}    Robot

Get Substring With End Only
    ${result} =    Get Substring    Hello Robot    end=5
    Should be equal    ${result}    Hello

Get Substring with empty string as start index is deprecated
    ${result} =    Get Substring    Hello Robot    ${EMPTY}    5
    Should be equal    ${result}    Hello

Get Substring With Invalid Start
    [Documentation]    FAIL ValueError: Argument 'start' got value 'invalid' that cannot be converted to integer, '' or None.
    Get Substring    Hello Robot    invalid
    Get Substring    ${{b'Hello Robot'}}    invalid

Get Substring With Invalid End
    [Documentation]    FAIL ValueError: Argument 'end' got value 'invalid' that cannot be converted to integer, '' or None.
    Get Substring    Hello Robot    2    invalid
    Get Substring    ${{b'Hello Robot'}}    2    invalid

Get Substring with bytes
    ${result} =    Get Substring    ${{b'Hi Robot'}}    0     2
    Should be equal    ${result}    ${{b'Hi'}}
    ${result} =    Get Substring    ${{b'Hi Robot'}}   -3    -1
    Should be equal    ${result}    ${{b'bo'}}
    ${result} =    Get Substring    ${{b'Hi Robot'}}    3
    Should be equal    ${result}    ${{b'Robot'}}
    ${result} =    Get Substring    ${{b'Hi Robot'}}    end=2
    Should be equal    ${result}    ${{b'Hi'}}

Strip String
    ${result} =    Strip String    ${SPACE}${SPACE}Hello${SPACE}
    Should be equal    ${result}    Hello

Strip String Left
    ${result} =    Strip String    ${SPACE}${SPACE}Hello${SPACE}    mode=left
    Should be equal    ${result}    Hello${SPACE}

Strip String Right
    ${result} =    Strip String    ${SPACE}${SPACE}Hello${SPACE}    mode=RiGht
    Should be equal    ${result}    ${SPACE}${SPACE}Hello

Strip String None
    ${result} =    Strip String    ${SPACE}${SPACE}Hello${SPACE}    mode=none
    Should be equal    ${result}    ${SPACE}${SPACE}Hello${SPACE}

Strip String With Invalid Mode
    [Documentation]    FAIL ValueError: Argument 'mode' got value 'invalid' that cannot be converted to 'left', 'right', 'both' or 'none'.
    Strip String  Hello  invalid

Strip String With Given Characters
    ${result} =    Strip String    aabaHelloeee    characters=abe
    Should be equal    ${result}    Hello

Strip String With Given Characters none
    ${result} =    Strip String    none123noneee    characters=none
    Should be equal    ${result}    123

Strip String with bytes
    ${result} =    Strip String    ${{b" Hello\t\n "}}
    Should be equal    ${result}    Hello    type=bytes
    ${result} =    Strip String    ${{b"-+-Hel-+-lo-+-"}}    left    ${{b"+-"}}
    Should be equal    ${result}    Hel-+-lo-+-    type=bytes
    ${result} =    Strip String    ${{b"-+-Hel-+-lo-+-"}}    right    +-=#%_
    Should be equal    ${result}    -+-Hel-+-lo    type=bytes

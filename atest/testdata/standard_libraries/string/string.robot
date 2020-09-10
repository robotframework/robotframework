*** Settings ***
Library           String

*** Variables ***
${NSN}            nokia_siemens_networks
${TEXT IN COLUMNS}    robot\tframework\nis\tgood\tfor\ttesting
${FIRST LINE}     robot\tframework
${SECOND LINE}    is\tgood\tfor\ttesting

*** Test Cases ***
Fetch From Left
    ${result} =    Fetch From Left    ${NSN}    _siemens
    Should be Equal    ${result}    nokia

Fetch From Right
    ${result} =    Fetch From Right    ${NSN}    _siemens_
    Should Be Equal    ${result}    networks

Get Line
    ${result} =    Get Line    ${TEXT IN COLUMNS}    0
    Should be equal    ${result}    ${FIRST LINE}
    ${result} =    Get Line    ${TEXT IN COLUMNS}    1
    Should be equal    ${result}    ${SECOND LINE}

Get Line Count
    ${result} =    Get Line Count    ${EMPTY}
    Should be equal as integers    ${result}    ${0}
    ${result} =    Get Line Count    ${SPACE}
    Should be equal as integers    ${result}    ${1}
    ${result} =    Get Line Count    ${TEXT IN COLUMNS}
    Should be equal as integers    ${result}    2

Split To Lines
    @{result} =    Split To Lines    ${TEXT IN COLUMNS}
    Length Should Be    ${result}    2
    Should be equal    ${result}[0]    ${FIRST LINE}
    Should be equal    ${result}[1]    ${SECOND LINE}

Split To Lines With Start Only
    @{result} =    Split To Lines    ${TEXT IN COLUMNS}    1
    Should be equal    ${result}[0]    ${SECOND LINE}

Split To Lines With Start And End
    @{result} =    Split To Lines    ${TEXT IN COLUMNS}    0    1
    Length Should Be    ${result}    1
    Should be equal    ${result}[0]    ${FIRST LINE}

Split To Lines With End Only
    @{result} =    Split To Lines    ${TEXT IN COLUMNS}    ${EMPTY}    1
    Length Should Be    ${result}    1
    Should be equal    ${result}[0]    ${FIRST LINE}

Split To Lines With Negative Values
    @{result} =    Split To Lines    ${TEXT IN COLUMNS}    -1
    Length Should Be    ${result}    1
    Should be equal    ${result}[0]    ${SECOND LINE}

Split To Lines With Invalid Start
    [Documentation]    FAIL ValueError: Cannot convert 'start' argument 'invalid' to an integer.
    Split To Lines    ${TEXT IN COLUMNS}    invalid

Split To Lines With Invalid End
    [Documentation]    FAIL ValueError: Cannot convert 'end' argument 'invalid' to an integer.
    Split To Lines    ${TEXT IN COLUMNS}    0    invalid

Get Substring
    ${result} =    Get Substring    Robot    0    2
    Should be equal    ${result}    Ro

Get Substring With Negative Values
    ${result} =    Get Substring    Hello Robot    -3    -1
    Should be equal    ${result}    bo

Get Substring With Start Only
    ${result} =    Get Substring    Hello Robot    6
    Should be equal    ${result}    Robot

Get Substring With Empty Start
    ${result} =    Get Substring    Hello Robot    ${EMPTY}    5
    Should be equal    ${result}    Hello

Get Substring With Invalid Start
    [Documentation]    FAIL ValueError: Cannot convert 'start' argument 'invalid' to an integer.
    Get Substring    Hello Robot    invalid

Get Substring With Invalid End
    [Documentation]    FAIL ValueError: Cannot convert 'end' argument 'invalid' to an integer.
    Get Substring    Hello Robot    2    invalid

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
    [Documentation]    FAIL ValueError: Invalid mode 'invalid'.
    Strip String  Hello  invalid

Strip String With Given Characters
    ${result} =    Strip String    aabaHelloeee    characters=abe
    Should be equal    ${result}    Hello

Strip String With Given Characters none
    ${result} =    Strip String    none123noneee    characters=none
    Should be equal    ${result}    123

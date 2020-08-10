*** Settings ***
Library                       robot_keyword_Annotations.py

*** Keywords ***
Integer
    [Arguments]    ${argument: Integer}    ${expected}=${Empty}
    Validate Type     ${argument}    ${expected}

Int
    [Arguments]    ${argument: INT}    ${expected}=${Empty}
    Validate Type     ${argument}    ${expected}

Long
    [Arguments]    ${argument: lOnG}    ${expected}=${Empty}
    Validate Type     ${argument}    ${expected}

Float
    [Arguments]    ${argument: Float}    ${expected}=${Empty}
    Validate Type     ${argument}    ${expected}

Double
    [Arguments]    ${argument: Float}    ${expected}=${Empty}
    Validate Type     ${argument}    ${expected}

Decimal
    [Arguments]    ${argument: DECIMAL}    ${expected}=${Empty}
    Validate Type     ${argument}    ${expected}

Boolean
    [Arguments]    ${argument: Boolean}    ${expected}=${Empty}
    Validate Type     ${argument}    ${expected}

Bool
    [Arguments]    ${argument: Bool}    ${expected}=${Empty}
    Validate Type     ${argument}    ${expected}

String
    [Arguments]    ${argument:String}    ${expected}=${Empty}
    Validate Type     ${argument}    ${expected}

Bytes
    [Arguments]    ${argument:BYTES}    ${expected}=${Empty}
    Validate Type     ${argument}    ${expected}

Bytearray
    [Arguments]    ${argument: ByteArray}    ${expected}=${Empty}
    Validate Type     ${argument}    ${expected}

Datetime
    [Arguments]    ${argument: DateTime}    ${expected}=${Empty}
    Validate Type     ${argument}    ${expected}

Date
    [Arguments]    ${argument: Date}    ${expected}=${Empty}
    Validate Type     ${argument}    ${expected}

Timedelta
    [Arguments]    ${argument: TimeDelta}    ${expected}=${Empty}
    Validate Type     ${argument}    ${expected}

List
    [Arguments]    ${argument: List}    ${expected}=${Empty}
    Validate Type     ${argument}    ${expected}

Tuple
    [Arguments]    ${argument: TUPLE}    ${expected}=${Empty}
    Validate Type     ${argument}    ${expected}

Dictionary
    [Arguments]    ${argument: Dictionary}    ${expected}=${Empty}
    Validate Type     ${argument}    ${expected}

Dict
    [Arguments]    ${argument: Dict}    ${expected}=${Empty}
    Validate Type     ${argument}    ${expected}

Set
    [Arguments]    ${argument: Set}    ${expected}=${Empty}
    Validate Type     ${argument}    ${expected}

Map
    [Arguments]    ${argument: Map}    ${expected}=${Empty}
    Validate Type     ${argument}    ${expected}

Frozenset
    [Arguments]    ${argument: FrozenSet}    ${expected}=${Empty}
    Validate Type     ${argument}    ${expected}

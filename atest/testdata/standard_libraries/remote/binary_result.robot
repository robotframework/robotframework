*** Settings ***
Library           Remote    127.0.0.1:${PORT}
Library           String
Suite Setup       Set Log Level    DEBUG

*** Variables ***
${PORT}           8270

*** Test Cases ***
Returned
    [Template]    Binary Should Be Returned Correctly
    \x00\x01\x02    0    1    2
    RF    82    70
    \xe4\xff    228    255
    ${EMPTY}

Returned in list
    ${result} =    Return Binary List    0    1    82    255
    Byte String Should Be Equal    ${result[0]}    \x00
    Byte String Should Be Equal    ${result[1]}    \x01
    Byte String Should Be Equal    ${result[2]}    R
    Byte String Should Be Equal    ${result[3]}    \xff

Returned in dict
    ${result} =    Return Binary Dict    a=0    b=1    R=82    ff=255
    Byte String Should Be Equal    ${result['a']}    \x00
    Byte String Should Be Equal    ${result['b']}    \x01
    Byte String Should Be Equal    ${result['R']}    R
    Byte String Should Be Equal    ${result['ff']}    \xff

Returned in nested structure
    ${result} =    Return Nested Binary    0    1    c=2    R=82
    Length Should Be    ${result}    3
    Byte String Should Be Equal    ${result[0]}    \x00
    Byte String Should Be Equal    ${result[1]}    \x01
    Length Should Be    ${result[2]}    4
    Byte String Should Be Equal    ${result[2]['c']}    \x02
    Byte String Should Be Equal    ${result[2]['R']}    R
    Length Should Be    ${result[2]['list']}    2
    Byte String Should Be Equal    ${result[2]['list'][0]}    \x00
    Byte String Should Be Equal    ${result[2]['list'][1]}    \x01
    Length Should Be    ${result[2]['dict']}    3
    Byte String Should Be Equal    ${result[2]['dict']['c']}    \x02
    Byte String Should Be Equal    ${result[2]['dict']['R']}    R
    Length Should Be    ${result[2]['dict']['list']}    2
    Byte String Should Be Equal    ${result[2]['dict']['list'][0]}    \x00
    Byte String Should Be Equal    ${result[2]['dict']['list'][1]}    \x01

Logged
    [Template]    Log Binary
    0    0    7
    82    70
    @{EMPTY}

Failed
    [Documentation]    FAIL Error: RF
    Fail Binary    82    0    0    7    70


*** Keywords ***
Binary Should Be Returned Correctly
    [Arguments]    ${expected}    @{ordinals}
    ${result} =    Return Binary    @{ordinals}
    Byte String Should Be Equal    ${result}    ${expected}

Byte String Should Be Equal
    [Arguments]    ${bytes}    ${expected}
    ${expected} =    Convert To Bytes    ${expected}
    Should Be Equal    ${bytes}    ${expected}
    Should Be Byte String    ${bytes}

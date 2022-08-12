*** Settings ***
Library           String

*** Test Cases ***
Replace String
    ${result} =    Replace String    Robot Framework    Frame    Class
    Should be equal    ${result}    Robot Classwork
    ${result} =    Replace String    Robot Framework    o    0    2
    Should be equal    ${result}    R0b0t Framework

Replace String Not Found
    ${result} =    Replace String    Robot    bat    bit
    Should be equal    ${result}    Robot

Replace String With Empty String
    ${result} =    Replace String    Robot Framework    Framework    ${EMPTY}
    Should be equal    ${result}    Robot${SPACE}

Replace String With Count 0
    ${result} =    Replace String    Robot Framework    Frame    Class    0
    Should Be Equal    ${result}    Robot Framework

Replace String With Invalid Count
    [Documentation]    FAIL ValueError: Cannot convert 'count' argument 'invalid' to an integer.
    Replace String    abc    b    c    invalid

Replace String Using Regexp
    ${result} =    Replace String Using Regexp    Robot Framework    F.*k    Class
    Should be equal    ${result}    Robot Class
    ${result} =    Replace String Using Regexp    Robot Framework    f.*k    Class    flags=IGNORECASE
    Should be equal    ${result}    Robot Class
    ${result} =    Replace String Using Regexp    Robot Framework    o\\w    foo    2
    Should be equal    ${result}    Rfoofoo Framework
    ${result} =    Replace String Using Regexp    Robot Framework    O\\w    foo    2    flags=IGNORECASE
    Should be equal    ${result}    Rfoofoo Framework

Replace String Using Regexp With Count 0
    ${result} =    Replace String Using Regexp    Robot Framework    F.*k    Class    0
    Should be equal    ${result}    Robot Framework

Replace String Using Regexp Not Found
    ${result} =    Replace String Using Regexp    Robot Framework    Fnot.*k    Class
    Should be equal    ${result}    Robot Framework

Replace String Using Regexp When Count Is Invalid
    [Documentation]    FAIL ValueError: Cannot convert 'count' argument 'invalid' to an integer.
    Replace String Using Regexp    Robot Framework    .*    foo    invalid

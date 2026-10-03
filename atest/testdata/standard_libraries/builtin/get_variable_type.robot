*** Settings ***
Library         Collections

*** Variables ***
${STRING}       hello
${INTEGER}      ${42}
${FLOAT}        ${1.5}
${BOOLEAN}      ${True}

*** Test Cases ***
String
    ${type} =    Get Variable Type    ${STRING}
    Should Be Equal    ${type}    string

Integer
    ${type} =    Get Variable Type    ${INTEGER}
    Should Be Equal    ${type}    integer

Float
    ${type} =    Get Variable Type    ${FLOAT}
    Should Be Equal    ${type}    float

Boolean
    ${type} =    Get Variable Type    ${BOOLEAN}
    Should Be Equal    ${type}    boolean

List
    ${value} =    Create List    1    2
    ${type} =    Get Variable Type    ${value}
    Should Be Equal    ${type}    list

Dictionary
    ${value} =    Create Dictionary    a=1
    ${type} =    Get Variable Type    ${value}
    Should Be Equal    ${type}    dictionary

Tuple
    ${value} =    Evaluate    (1, 2)
    ${type} =    Get Variable Type    ${value}
    Should Be Equal    ${type}    tuple

Set
    ${value} =    Evaluate    {1, 2}
    ${type} =    Get Variable Type    ${value}
    Should Be Equal    ${type}    set

None
    ${type} =    Get Variable Type    ${NONE}
    Should Be Equal    ${type}    none

Custom object
    ${value} =    Evaluate    object()
    ${type} =    Get Variable Type    ${value}
    Should Be Equal    ${type}    object
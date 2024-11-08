*** Settings ***
Variables         non_string_variables.py
Test Template     Should Be Equal

*** Test Cases ***
Numbers
    [Documentation]  I can has ${INTEGER} and ${FLOAT}?
    ${INTEGER}        ${42}
    -${INTEGER}-      -42-
    ${FLOAT}          ${3.14}
    -${FLOAT}-        -3.14-

Bytes
    [Documentation]  We has ${BYTES}!
    ${BYTES}          ${BYTES}
    ${BYTEARRAY}      ${BYTEARRAY}
    ${LOW BYTES}      ${LOW BYTES}
    -${BYTES}-        -hyvä-
    -${BYTEARRAY}-    -hyvä-
    -${LOW BYTES}-    -\x00\x01\x02-

Bytes concatenated with bytes yields bytes
    [Documentation]    ${BYTES}${BYTEARRAY}
    ${BYTES}${BYTEARRAY}         ${{b'hyv\xe4hyv\xe4'}}
    ${BYTEARRAY}${BYTES}         ${{b'hyv\xe4hyv\xe4'}}
    ${BYTES}${{b'-'}}${BYTES}    ${{b'hyv\xe4-hyv\xe4'}}

Bytes string representation can be converted back to bytes
    [Documentation]    ${LOW BYTES}
    [Template]    NONE
    ${result} =    Convert To Bytes    ${BYTES}, ${LOW BYTES} and ${BYTEARRAY}
    Should Be Equal    ${result}    ${{b'hyv\xe4, \x00\x01\x02 and hyv\xe4'}}

Collections
    [Documentation]  ${LIST} ${DICT}
    -${LIST}-         -${LIST STR}-
    -${DICT}-         -${DICT STR}-

Misc
    [Documentation]  ${BOOLEAN} ${NONE} ${MODULE}
    -${BOOLEAN}-      -True-
    -${NONE}-         -None-
    -${MODULE}-       -${MODULE STR}-

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
    -${BYTES}-        -${BYTES STR}-
    -${BYTEARRAY}-    -${BYTES STR}-

Collections
    [Documentation]  ${LIST} ${DICT}
    -${LIST}-         -${LIST STR}-
    -${DICT}-         -${DICT STR}-

Misc
    [Documentation]  ${BOOLEAN} ${NONE} ${MODULE}
    -${BOOLEAN}-      -True-
    -${NONE}-         -None-
    -${MODULE}-       -${MODULE STR}-

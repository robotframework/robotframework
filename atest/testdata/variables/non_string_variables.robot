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

Byte string
    [Documentation]  We has ${BYTE STRING}!
    ${BYTE STRING}    ${BYTE STRING}
    -${BYTE STRING}-  -${BYTE STRING STR}-

Collections
    [Documentation]  ${LIST} ${DICT}
    -${LIST}-         -${LIST STR}-
    -${DICT}-         -${DICT STR}-

Misc
    [Documentation]  ${BOOLEAN} ${NONE} ${MODULE}
    -${BOOLEAN}-      -True-
    -${NONE}-         -None-
    -${MODULE}-       -${MODULE STR}-

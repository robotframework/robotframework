*** Settings ***
Variables       variable.py

*** Test Cases ***
TC
    Should Be Equal  ${SUITE}  suite2
    Should Be Equal  ${SUITE 2}  suite2
    Variable Should Not Exist  ${SUITE 1}
    Variable Should Not Exist  ${SUITE 11}
    Variable Should Not Exist  ${SUITE 3}
    Variable Should Not Exist  ${SUITE 31}
    Variable Should Not Exist  ${SUITE 32}


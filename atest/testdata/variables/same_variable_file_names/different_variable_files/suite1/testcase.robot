*** Settings ***
Variables       variable.py

*** Test Cases ***
TC
    Should Be Equal  ${SUITE}  suite1
    Should Be Equal  ${SUITE 1}  suite1
    Variable Should Not Exist  ${SUITE 11}
    Variable Should Not Exist  ${SUITE 2}
    Variable Should Not Exist  ${SUITE 3}
    Variable Should Not Exist  ${SUITE 31}
    Variable Should Not Exist  ${SUITE 32}


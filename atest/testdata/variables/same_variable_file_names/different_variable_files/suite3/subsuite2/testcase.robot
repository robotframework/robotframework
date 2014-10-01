*** Settings ***
Variables       variable.py

*** Test Cases ***
TC
    Should Be Equal  ${SUITE}  suite3.subsuite2
    Should Be Equal  ${SUITE 32}  suite3.subsuite2
    Variable Should Not Exist  ${SUITE 1}
    Variable Should Not Exist  ${SUITE 11}
    Variable Should Not Exist  ${SUITE 2}
    Variable Should Not Exist  ${SUITE 3}
    Variable Should Not Exist  ${SUITE 31}


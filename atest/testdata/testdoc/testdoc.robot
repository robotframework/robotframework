*** Settings ***
Documentation   Documentation with ${CURDIR}
Library         nonex
Resource        exnon
Variables       xxxxx

*** Variables ***
${FOO}     ${CURDIR}
${BAR}     ${NONEX}

*** Test Cases ***
Example
    Log    ${CURDIR}
    Nön-existing nön-ÄSCII keywörd

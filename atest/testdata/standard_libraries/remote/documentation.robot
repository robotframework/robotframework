*** Settings ***
Library           Remote    127.0.0.1:${PORT}

*** Variables ***
${PORT}           8270

*** Test Cases ***
Empty
    Empty

Single
    Single    1

Multi
    Multi    1
    Multi    1    2
    Multi    1    2    3    4

Nön-ÄSCII
    Nön-ÄSCII

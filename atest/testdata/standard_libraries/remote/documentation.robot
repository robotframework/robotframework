*** Settings ***
Library           Remote    127.0.0.1:${PORT}

*** Variables ***
${PORT}           8270

*** Test Cases ***
Empty
    Empty

Single line
    Single line

Multi line
    Multi line

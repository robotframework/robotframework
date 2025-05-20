*** Settings ***
Library         CustomDir.py

*** Test Cases ***
Normal keyword
    Normal    arg

Keyword implemented via getattr
    Via getattr    arg

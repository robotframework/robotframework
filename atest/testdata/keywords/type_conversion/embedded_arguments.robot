*** Settings ***
Library                  EmbeddedArguments.py

*** Test Cases ***
Types via annotations
    1 + 2 = 3
    2 + 2 = 4

Types via @keyword
    2 - 1 = 1
    2 - 2 = 0

Types via defaults
    1 * 2 = 2
    2 * 2 = 4

*** Settings ***
Force Tags        require-py3
Library           LibraryWithKeywordWraps.py

*** Test Cases ***
Keyword Decorator With Wraps
    Keyword With Wraps    42

Keyword Decorator With Wraps Mismatched Type
    Run Keyword And Expect Error    *Argument 'arg' got value 'string' that cannot be converted to integer.    Keyword With Wraps    string

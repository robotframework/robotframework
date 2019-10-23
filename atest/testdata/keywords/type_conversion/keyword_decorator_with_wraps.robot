*** Settings ***
Library           LibraryWithKeywordWraps.py

*** Test Cases ***
Keyword Decorator With Wraps
    Keyword With Wraps    42

Keyword Decorator With Wraps Mismatched Type
    [Documentation]    FAIL ValueError: Argument 'arg' got value 'string' that cannot be converted to integer.
    Keyword With Wraps    string

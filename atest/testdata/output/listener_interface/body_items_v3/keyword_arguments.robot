*** Settings ***
Library                Library.py

*** Variables ***
${STATE}               new

*** Test Cases ***
Valid arguments
    Library keyword    initial    args    are    overwritten

Too many arguments
    [Documentation]    FAIL
    ...    Several failures occurred:
    ...
    ...    1) Keyword 'Library.Library Keyword' expected 0 to 4 arguments, got 7.
    ...
    ...    2) Keyword 'Library.Library Keyword' expected 0 to 4 arguments, got 100.
    Library keyword    initial    args    are    overwritten

Conversion error
    [Documentation]    FAIL
    ...    Several failures occurred:
    ...
    ...    1) ValueError: Argument 'number' got value 'not a number' that cannot be converted to integer.
    ...
    ...    2) ValueError: Argument 'number' got value 'bad' that cannot be converted to integer.
    Library keyword    initial    args    are    overwritten

Positional after named
    [Documentation]    FAIL
    ...    Keyword 'Library.Library Keyword' got positional argument after named arguments.
    Library keyword    initial    args    are    overwritten

*** Settings ***
Library            KeywordsImplementedInC.py

*** Test Cases ***
Use with correct arguments
    ${result} =    Eq    foo    foo
    Should Be True    ${result} is True
    ${result} =    Eq    foo    bar
    Should Be True    ${result} is False
    ${result} =    Length    Hello, world!
    Should Be True    ${result} == 13
    Print    This is    a bit weird    ...

Use with incorrect arguments
    [Documentation]    Error depends on the interpreter.
    Eq    too    many    args

Built-ins not set to attributes are not exposes
    [Documentation]    FAIL    No keyword with name 'Sum' found.
    Sum

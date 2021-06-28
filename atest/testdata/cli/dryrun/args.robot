*** Settings ***
Library     Library.py
Resource    resource.robot

*** Test Cases ***
Valid positional args
    Normal args    1
    Normal args    1    2
    Normal and varargs    1    2    3    4
    Normal and varargs and kwargs   1    2    3    4

Too few arguments
    [Documentation]  FAIL Keyword 'BuiltIn.Should Be Equal' expected 2 to 8 arguments, got 1.
    Should Be Equal    1

Too few arguments for UK
    [Documentation]  FAIL Keyword 'resource.Anarchy in the UK' expected 3 arguments, got 1.
    Anarchy in the UK    foo

Too many arguments
    [Documentation]  FAIL  Keyword 'BuiltIn.No Operation' expected 0 arguments, got 2.
    No Operation    ${foo}    bar

Valid named args
    Normal args    1      b=2
    Normal args    a=1
    Normal args    a=1    b=2
    Normal args    b=2    a=1
    Normal and varargs    1      b=2
    Normal and varargs    a=1
    Normal and varargs    a=1    b=2
    Normal and varargs    b=2    a=1
    Normal and varargs and kwargs    1      b=2
    Normal and varargs and kwargs    a=1
    Normal and varargs and kwargs    a=1    c=3
    Normal and varargs and kwargs    a=1    b=2    c=3
    Normal and varargs and kwargs    d=4    c=3    b=2    a=1

Invalid named args
    [Documentation]  FAIL Several failures occurred:\n\n
    ...  1) Keyword 'Library.Normal Args' got unexpected named argument 'c'.\n\n
    ...  2) Keyword 'Library.Normal Args' got positional argument after named arguments.\n\n
    ...  3) Keyword 'Library.Normal Args' got unexpected named argument 'c'.\n\n
    ...  4) Keyword 'Library.Normal And Varargs' got unexpected named argument 'c'.\n\n
    ...  5) Keyword 'Library.Normal And Varargs And Kwargs' got positional argument after named arguments.
    Normal args    a=1    c=3
    Normal args    a=1    2
    Normal args    a=1    b=2    c=3
    Normal and varargs    a=1    b=2    c=3
    Normal and varargs and kwargs    a=1    c=3    xxx

*** Settings ***
Library                  overloads.py
Resource                 conversion.resource

*** Test Cases ***
Annotated
    foo    1    ${1}
    foo    None    ${None}
    TRY
        foo    a    a
    EXCEPT     ValueError: Couldn't convert to any overload:\n \ Argument 'argument' got value 'a' that cannot be converted to integer.\n \ Argument 'argument' got value 'a' that cannot be converted to None.
        No Operation
    END


Unannotated
    bar    1    ${1}
    bar    None    ${None}
    TRY
        foo    a    a
    EXCEPT     ValueError: Couldn't convert to any overload:\n \ Argument 'argument' got value 'a' that cannot be converted to integer.\n \ Argument 'argument' got value 'a' that cannot be converted to None.
        No Operation
    END

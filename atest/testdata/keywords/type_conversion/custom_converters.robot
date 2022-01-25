*** Settings ***
Library           CustomConverters.py
Library           CustomConvertersWithLibraryDecorator.py
Library           InvalidCustomConverters.py
Resource          conversion.resource

*** Test Cases ***
New conversion
    Number    one    1
    Number    two    2

Override existing conversion
    True     True
    True     whatever
    True     ${True}
    True     ${1}
    False    False
    False    epätosi
    False    ☹
    False    ${False}
    False    ${0}

Subclasses
    US date      11/30/2021    2021-11-30
    FI date      30.11.2021    2021-11-30
    Dates        11/30/2021    30.11.2021

Class as converter
    Class as converter               Robot    Hello, Robot!
    Class with hints as converter    ${42}    ${42}
    Class with hints as converter    42       42

Custom in Union
    Number or int    ${1}
    Number or int    1
    Number or int    one
    Int or number    ${1}
    Int or number    1
    Int or number    one

Accept subscripted generics
    Accept subscripted generics    ${{[1, 2, 3]}}    ${6}

Failing conversion
    [Template]    Conversion should fail
    Number     wrong         type=Number     error=Don't know number 'wrong'.
    US date    30.11.2021    type=UsDate     error=Value does not match '%m/%d/%Y'.
    US date    ${666}        type=UsDate     error=TypeError: Only strings accepted!    arg_type=integer
    FI date    ${666}        type=FiDate     arg_type=integer
    True       ${1.0}        type=boolean    arg_type=float
    Class with hints as converter
    ...        ${1.2}        type=ClassWithHintsAsConverter    arg_type=float

Invalid converters
    Invalid    a    b    c    d

Non-type annotation
    Non type annotation    x    x
    Non type annotation    ${2}

Using library decorator
    Using library decorator    one    1
    Using library decorator    two    2

Invalid converter dictionary
    Keyword in library with invalid converters    666

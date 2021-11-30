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

Failing conversion
    [Template]    Conversion should fail
    Number     wrong         type=Number     error=ValueError: Don't know number 'wrong'.
    US date    30.11.2021    type=UsDate     error=Value does not match '%m/%d/%Y'.
    FI date    ${666}        type=FiDate     error=TypeError: Only strings accepted!    arg_type=integer

Invalid converter
    [Template]    Conversion should fail
    Invalid    xxx           type=Invalid    error=TypeError: 'int' object is not callable

Non-type annotation
    Non type annotation    x    x
    Non type annotation    ${2}

Using library decorator
    Using library decorator    one    1
    Using library decorator    two    2

Invalid converter dictionary
    Keyword in library with invalid converters    666

*** Settings ***
Library           CustomConverters.py
Library           CustomConverters.StatefulLibrary
Library           CustomConverters.StatefulGlobalLibrary
Library           CustomConvertersWithLibraryDecorator.py
Library           CustomConvertersWithDynamicLibrary.py
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

With generics
    With generics
    ...    ['one', 'two', 'three']
    ...    ('28.9.2022', '9/28/2022')
    ...    {'one': '28.9.2022'}
    ...    {'one', 'two', 'three'}
    With generics
    ...    ${{['one', 'two', 'three']}}
    ...    ${{('28.9.2022', '9/28/2022')}}
    ...    ${{{'one': '28.9.2022'}}}
    ...    ${{{'one', 'two', 'three'}}}

With TypedDict
    TypedDict    {'fi': '29.9.2022', 'us': '9/29/2022'}

Failing conversion
    [Template]    Conversion should fail
    Number     wrong         type=Number     error=Don't know number 'wrong'.
    US date    30.11.2021    type=UsDate     error=Value does not match '%m/%d/%Y'.
    US date    ${666}        type=UsDate     error=TypeError: Only strings accepted!    arg_type=integer
    FI date    ${666}        type=FiDate     arg_type=integer
    True       ${1.0}        type=boolean    arg_type=float
    Class with hints as converter
    ...        ${1.2}        type=ClassWithHintsAsConverter    arg_type=float

`None` as strict converter
    Strict    ${{CustomConverters.Strict()}}
    Conversion should fail    Strict    wrong type
    ...    type=Strict    error=TypeError: Only Strict instances are accepted, got string.

Only vararg
    Only var arg    10    10

With library as argument to converter
    String    ${123}

Test scope library instance is reset between test 1
    Multiply    2    ${2}
    Multiply    2    ${4}
    Multiply    4    ${12}

Test scope library instance is reset between test 2
    Multiply    2    ${2}

Global scope library instance is not reset between test 1
    Global Multiply    2    ${2}
    Global Multiply    2    ${4}

Global scope library instance is not reset between test 2
    Global Multiply    4    ${12}


Invalid converters
    Invalid    a    b    c    d

Non-type annotation
    Non type annotation    x    x
    Non type annotation    ${2}

Using library decorator
    Using library decorator    one    1
    Using library decorator    expected=2    value=two

With embedded arguments
    Embedded "one" should be equal to "1"
    Embedded "two" should be equal to "2"

Failing conversion with embedded arguments
    [Documentation]    FAIL    ValueError: Argument 'value' got value 'bad' that cannot be converted to Number: Don't know number 'bad'.
    [Tags]    no-dry-run
    Embedded "bad" should be equal to "1"

With dynamic library
    Dynamic keyword    one    1
    Dynamic keyword    expected=2    argument=two

Failing conversion with dynamic library
    [Template]    Conversion should fail
    Dynamic keyword    bad    1    type=Number     error=Don't know number 'bad'.

Invalid converter dictionary
    Keyword in library with invalid converters    666

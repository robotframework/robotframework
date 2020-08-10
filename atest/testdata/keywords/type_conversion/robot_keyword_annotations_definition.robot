*** Settings ***
Library                       robot_keyword_Annotations.py

*** Keywords ***
Integer
    [Arguments]    ${argument:int}    ${expected}=${Empty}
    Validate Type     ${argument}    ${expected}

Integral
    [Arguments]    ${argument:Integral}    ${expected}=${Empty}
    Validate Type     ${argument}    ${expected}

Float
    [Arguments]    ${argument:float}    ${expected}=${Empty}
    Validate Type     ${argument}    ${expected}

Real
    [Arguments]    ${argument:Real}    ${expected}=${Empty}
    Validate Type     ${argument}    ${expected}

Decimal
    [Arguments]    ${argument:Decimal}    ${expected}=${Empty}
    Validate Type     ${argument}    ${expected}

Boolean
    [Arguments]    ${argument:bool}    ${expected}=${Empty}
    Validate Type     ${argument}    ${expected}

String
    [Arguments]    ${argument:str}    ${expected}=${Empty}
    Validate Type     ${argument}    ${expected}

Bytes
    [Arguments]    ${argument:bytes}    ${expected}=${Empty}
    Validate Type     ${argument}    ${expected}

ByteString
    [Arguments]    ${argument:ByteString}    ${expected}=${Empty}
    Validate Type     ${argument}    ${expected}

Bytearray
    [Arguments]    ${argument:bytearray}    ${expected}=${Empty}
    Validate Type     ${argument}    ${expected}

Datetime
    [Arguments]    ${argument:datetime}    ${expected}=${Empty}
    Validate Type     ${argument}    ${expected}

Date
    [Arguments]    ${argument:date}    ${expected}=${Empty}
    Validate Type     ${argument}    ${expected}

Timedelta
    [Arguments]    ${argument:timedelta}    ${expected}=${Empty}
    Validate Type     ${argument}    ${expected}

Enum
    [Arguments]    ${argument:robot_keyword_Annotations.MyEnum}    ${expected}=${Empty}
    Validate Type     ${argument}    ${expected}

Nonetype
    [Arguments]    ${argument:None}    ${expected}=${Empty}
    Validate Type     ${argument}    ${expected}

List
    [Arguments]    ${argument:list}    ${expected}=${Empty}
    Validate Type     ${argument}    ${expected}

Sequence
    [Arguments]    ${argument:Sequence}    ${expected}=${Empty}
    Validate Type     ${argument}    ${expected}

MutableSequence
    [Arguments]    ${argument:MutableSequence}    ${expected}=${Empty}
    Validate Type     ${argument}    ${expected}

Tuple
    [Arguments]    ${argument:tuple}    ${expected}=${Empty}
    Validate Type     ${argument}    ${expected}

Dictionary
    [Arguments]    ${argument:dict}    ${expected}=${Empty}
    Validate Type     ${argument}    ${expected}

Mapping
    [Arguments]    ${argument:Mapping}    ${expected}=${Empty}
    Validate Type     ${argument}    ${expected}

MutableMapping
    [Arguments]    ${argument:MutableMapping}    ${expected}=${Empty}
    Validate Type     ${argument}    ${expected}

Set
    [Arguments]    ${argument:set}    ${expected}=${Empty}
    Validate Type     ${argument}    ${expected}

Set Abc
    [Arguments]    ${argument:abc.Set}    ${expected}=${Empty}
    Validate Type     ${argument}    ${expected}

Mutable Set
    [Arguments]    ${argument:abc.MutableSet}    ${expected}=${Empty}
    Validate Type     ${argument}    ${expected}

Frozenset
    [Arguments]    ${argument:frozenset}    ${expected}=${Empty}
    Validate Type     ${argument}    ${expected}

Unknown
    [Arguments]    ${argument:Unknown}    ${expected}=${Empty}
    Validate Type     ${argument}    ${expected}

Non Type
    [Arguments]    ${argument:'this is string, not type'}    ${expected}=${Empty}
    Validate Type     ${argument}    ${expected}

Invalid
    [Arguments]    ${argument:'import sys'}    ${expected}=${Empty}
    Validate Type     ${argument}    ${expected}

Varargs
    [Arguments]    @{argument:int}    ${expected}=${Empty}
    Validate Type     ${argument}    ${expected}


Kwargs
    [Arguments]    ${expected}=${Empty}    &{argument:int}
    Validate Type     ${argument}    ${expected}


Kwonly
    [Arguments]    @{}    ${argument:float}    ${expected}=${Empty}
    Validate Type     ${argument}    ${expected}


None As Default
    [Arguments]   ${argument:list}=${Empty}    ${expected}=${Empty}
    Validate Type     ${argument}    ${expected}


Forward Referenced Concrete Type
    [Arguments]   ${argument:int}    ${expected}=${Empty}
    Validate Type     ${argument}    ${expected}

Return Value Annotation
    [Arguments]   ${argument:int}=${Empty}    ${expected}=${Empty}
    [Return]    ${argument:float}
    Validate Type     ${argument}    ${expected}
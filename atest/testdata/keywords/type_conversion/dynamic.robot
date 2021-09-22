*** Settings ***
Library                Dynamic.py
Resource               conversion.resource

*** Test Cases ***
List of types
    List of types      42                  42

Dict of types
    Dict of types      42                  Decimal(42)

List of aliases
    List of aliases    BÖÖ!!               b'B\\xd6\\xd6!!'

Dict of aliases
    Dict of aliases    {'a': 1, 'b': 2}    {'a': 1, 'b': 2}

Default values
    Default values
    Default values    1    middle=NONE    last=True
    Default values    1.5    1.5    not none    u'not none'    OFF    False
    Default values    x    u'x'    y    u'y'    z    u'z'

Kwonly defaults
    Kwonly defaults    first=1    last=True
    Kwonly defaults    last=FALSE    first_expected=42    first=42    last_expected=False
    Kwonly defaults    first=-1.1    first_expected=-1.1    last=not bool    last_expected=u'not bool'

Default values are not used if `get_keyword_types` returns `None`
    Default values when types are none    True     u'True'
    Default values when types are none    TRUE     u'TRUE'
    Default values when types are none    False    u'False'
    Default values when types are none    xxx      u'xxx'
